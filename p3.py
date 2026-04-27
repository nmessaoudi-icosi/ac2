import os
import csv
import math
import time
import random
from pathlib import Path
from datetime import datetime

import requests
import paho.mqtt.client as mqtt
from dotenv import load_dotenv


# ==========================================================
# Chargement sécurisé des clés depuis .env
# ==========================================================

load_dotenv()
load_dotenv()

CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID")

MQTT_CLIENT_ID = os.getenv("THINGSPEAK_MQTT_CLIENT_ID")
MQTT_USERNAME = os.getenv("THINGSPEAK_MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("THINGSPEAK_MQTT_PASSWORD")

READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY")



if not CHANNEL_ID:
    raise ValueError("THINGSPEAK_CHANNEL_ID manquant dans le fichier .env")

if not MQTT_CLIENT_ID or not MQTT_USERNAME or not MQTT_PASSWORD:
    raise ValueError("Identifiants MQTT ThingSpeak manquants dans le fichier .env")


# ==========================================================
# Configuration ThingSpeak MQTT
# ==========================================================

MQTT_BROKER = "mqtt3.thingspeak.com"
MQTT_PORT = 1883
MQTT_TOPIC = f"channels/{CHANNEL_ID}/publish"

READ_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds/last.json"


# ==========================================================
# Paramètres de simulation
# ==========================================================

INTERVAL_S = 20

PANEL_AREA_M2 = 1.6
PANEL_EFFICIENCY = 0.20
TEMP_COEFF = 0.004

BATTERY_CAPACITY_WH = 1200.0
TRACKER_STEP_DEG = 4

FIXED_PANEL_ANGLE = 35.0

CSV_FILE = Path("simulation_log.csv")


# ==========================================================
# États numériques exploitables dans ThingSpeak
# ==========================================================

STATE_CODES = {
    "AUTONOME": 0,
    "CHARGE_BATTERIE": 1,
    "APPORT_BATTERIE": 2,
    "IMPORT_RESEAU": 3,
    "INJECTION_RESEAU": 4,
    "PEAK_DEMAND": 5,
    "BATTERIE_FAIBLE": 6,
    "FAIBLE_PRODUCTION": 7,
}


STATE_LABELS = {
    0: "AUTONOME",
    1: "CHARGE_BATTERIE",
    2: "APPORT_BATTERIE",
    3: "IMPORT_RESEAU",
    4: "INJECTION_RESEAU",
    5: "PEAK_DEMAND",
    6: "BATTERIE_FAIBLE",
    7: "FAIBLE_PRODUCTION",
}


# ==========================================================
# Variables globales du système
# ==========================================================

panel_angle = 20.0
battery_wh = 600.0


# ==========================================================
# Fonctions utilitaires
# ==========================================================

def clamp(value, vmin, vmax):
    return max(vmin, min(value, vmax))


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ==========================================================
# Simulation météo
# ==========================================================

def weather_scenario(step):
    """
    Simule un scénario météo cyclique.
    Chaque cycle représente une journée accélérée.
    """

    cycle = step % 72

    if 18 <= cycle <= 26:
        return "CLOUDY"
    elif 38 <= cycle <= 44:
        return "STORM"
    elif 52 <= cycle <= 58:
        return "PARTIAL_SHADING"
    else:
        return "SUNNY"


def apply_weather_effect(irradiance, scenario):
    """
    Applique l'effet météo sur l'irradiance.
    """

    if scenario == "SUNNY":
        factor = random.uniform(0.90, 1.00)
    elif scenario == "CLOUDY":
        factor = random.uniform(0.55, 0.75)
    elif scenario == "STORM":
        factor = random.uniform(0.20, 0.40)
    elif scenario == "PARTIAL_SHADING":
        factor = random.uniform(0.40, 0.60)
    else:
        factor = 1.0

    return clamp(irradiance * factor, 0, 1000)


# ==========================================================
# Simulation environnementale
# ==========================================================

def simulate_environment(step):
    """
    Simule une journée simplifiée :
    - irradiance solaire
    - température
    - demande électrique
    - angle solaire
    - météo
    """

    phase = (step % 72) / 72.0
    sun_factor = max(0.0, math.sin(math.pi * phase))

    base_irradiance = 900 * sun_factor + random.uniform(-20, 20)
    base_irradiance = clamp(base_irradiance, 0, 1000)

    scenario = weather_scenario(step)
    irradiance = apply_weather_effect(base_irradiance, scenario)

    temperature = 20 + 12 * sun_factor + random.uniform(-1.5, 1.5)

    # Charge domestique : plus forte quand le soleil baisse
    load_power = 140 + 120 * (1 - sun_factor) + random.uniform(-20, 25)

    # Pic artificiel en soirée
    if 48 <= (step % 72) <= 60:
        load_power += random.uniform(60, 120)

    load_power = max(50, load_power)

    sun_angle = 15 + 60 * sun_factor

    return irradiance, temperature, load_power, sun_angle, scenario


# ==========================================================
# Modèle PV avec tracker et panneau fixe
# ==========================================================

def update_tracker(current_angle, target_angle, step_deg=TRACKER_STEP_DEG):
    if current_angle < target_angle:
        current_angle = min(current_angle + step_deg, target_angle)
    else:
        current_angle = max(current_angle - step_deg, target_angle)

    return current_angle


def compute_solar_power(irradiance, temperature, panel_angle_value, sun_angle):
    """
    Calcule la puissance solaire selon :
    - irradiance
    - température
    - surface du panneau
    - rendement
    - erreur d'orientation
    """

    tracking_error = abs(panel_angle_value - sun_angle)
    alignment = max(0.0, math.cos(math.radians(tracking_error)))

    temp_factor = 1 - TEMP_COEFF * max(0.0, temperature - 25)
    temp_factor = clamp(temp_factor, 0.75, 1.0)

    power = PANEL_AREA_M2 * irradiance * PANEL_EFFICIENCY * alignment * temp_factor

    return max(0.0, power)


def compute_tracker_gain(power_tracker, power_fixed):
    if power_fixed <= 0:
        return 0.0

    return ((power_tracker - power_fixed) / power_fixed) * 100.0


# ==========================================================
# Gestion énergie : batterie + réseau
# ==========================================================

def manage_energy(production_w, load_w, current_battery_wh):
    """
    Gère l'énergie :
    - surplus : charge batterie puis injection réseau
    - déficit : batterie puis import réseau

    Retourne :
    - nouvelle énergie batterie
    - batterie en %
    - puissance réseau
      > 0 : import réseau
      < 0 : injection réseau
    - état textuel
    """

    net_power_w = production_w - load_w
    delta_wh = net_power_w * INTERVAL_S / 3600.0
    grid_power_w = 0.0

    if delta_wh >= 0:
        charge_wh = min(delta_wh, BATTERY_CAPACITY_WH - current_battery_wh)
        current_battery_wh += charge_wh

        export_wh = delta_wh - charge_wh
        grid_power_w = -(export_wh * 3600.0 / INTERVAL_S)

        if export_wh > 0.1:
            state = "INJECTION_RESEAU"
        elif charge_wh > 0.1:
            state = "CHARGE_BATTERIE"
        else:
            state = "AUTONOME"

    else:
        need_wh = -delta_wh
        discharge_wh = min(need_wh, current_battery_wh)
        current_battery_wh -= discharge_wh

        import_wh = need_wh - discharge_wh
        grid_power_w = import_wh * 3600.0 / INTERVAL_S

        if import_wh > 0.1:
            state = "IMPORT_RESEAU"
        elif discharge_wh > 0.1:
            state = "APPORT_BATTERIE"
        else:
            state = "AUTONOME"

    battery_pct = 100.0 * current_battery_wh / BATTERY_CAPACITY_WH

    return current_battery_wh, battery_pct, grid_power_w, state


# ==========================================================
# Détection de peak + alertes
# ==========================================================

def detect_peak(load_power, solar_power, battery_pct):
    """
    Détecte un peak demand quand :
    - la demande dépasse fortement la production
    - et la batterie est faible ou moyenne
    """

    deficit = load_power - solar_power

    if deficit > 120 and battery_pct < 40:
        return 1

    if deficit > 180:
        return 1

    return 0


def generate_alerts(solar_power, load_power, battery_pct, grid_power, weather):
    alerts = []

    if battery_pct < 20:
        alerts.append("BATTERIE_FAIBLE")

    if load_power > solar_power + 120:
        alerts.append("PEAK_DEMAND")

    if grid_power > 150:
        alerts.append("IMPORT_RESEAU_ELEVE")

    if solar_power < 20:
        alerts.append("FAIBLE_PRODUCTION_PV")

    if weather in ["STORM", "PARTIAL_SHADING"]:
        alerts.append(f"METEO_{weather}")

    return alerts


def encode_state(state, peak, battery_pct, solar_power):
    """
    Convertit l'état système en code numérique pour ThingSpeak.
    """

    if peak == 1:
        return STATE_CODES["PEAK_DEMAND"]

    if battery_pct < 20:
        return STATE_CODES["BATTERIE_FAIBLE"]

    if solar_power < 20:
        return STATE_CODES["FAIBLE_PRODUCTION"]

    return STATE_CODES.get(state, -1)


# ==========================================================
# Sauvegarde CSV
# ==========================================================

def save_to_csv(row):
    file_exists = CSV_FILE.exists()

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


# ==========================================================
# ThingSpeak MQTT
# ==========================================================

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[MQTT] Connecté à ThingSpeak")
    else:
        print(f"[MQTT] Erreur de connexion. Code={rc}")


def on_publish(client, userdata, mid, reason_codes=None, properties=None):
    print(f"[MQTT] Message publié. mid={mid}")


def create_mqtt_client():
    client = mqtt.Client(
        client_id=MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv311
    )

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_publish = on_publish

    return client


def publish_to_thingspeak_mqtt(client, data):
    """
    Envoie les données vers ThingSpeak par MQTT.

    Organisation des fields :
    field1 = Irradiance W/m2
    field2 = Température °C
    field3 = Puissance tracker W
    field4 = Charge / demande W
    field5 = Batterie %
    field6 = Gain tracker %
    field7 = Peak detection 0/1
    field8 = État numérique
    """

    payload = (
        f"field1={data['irradiance']:.1f}"
        f"&field2={data['temperature']:.1f}"
        f"&field3={data['power_tracker']:.1f}"
        f"&field4={data['load_power']:.1f}"
        f"&field5={data['battery_pct']:.1f}"
        f"&field6={data['tracker_gain_pct']:.1f}"
        f"&field7={data['peak']}"
        f"&field8={data['state_code']}"
        f"&status={data['status']}"
    )

    result = client.publish(
        MQTT_TOPIC,
        payload=payload,
        qos=0,
        retain=False
    )

    return result, payload


# ==========================================================
# Lecture + analyse ThingSpeak
# ==========================================================

def read_last_from_thingspeak():
    if not READ_API_KEY:
        print("[READ] THINGSPEAK_READ_API_KEY absent. Lecture ignorée.")
        return None

    try:
        response = requests.get(
            READ_URL,
            params={"api_key": READ_API_KEY},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        print(f"[READ] Erreur lecture ThingSpeak : {e}")
        return None


def analyze_last_data(data):
    if not isinstance(data, dict):
        print("[READ] Donnée ThingSpeak invalide ou vide :", data)
        return

    irradiance = safe_float(data.get("field1"))
    temperature = safe_float(data.get("field2"))
    solar_power = safe_float(data.get("field3"))
    load_power = safe_float(data.get("field4"))
    battery_pct = safe_float(data.get("field5"))
    tracker_gain = safe_float(data.get("field6"))
    peak = int(safe_float(data.get("field7")))
    state_code = int(safe_float(data.get("field8")))

    state_label = STATE_LABELS.get(state_code, "UNKNOWN")

    print("\n----- Analyse dernière donnée ThingSpeak -----")
    print(f"Irradiance          : {irradiance:.1f} W/m²")
    print(f"Température         : {temperature:.1f} °C")
    print(f"Production tracker  : {solar_power:.1f} W")
    print(f"Demande énergétique : {load_power:.1f} W")
    print(f"Batterie            : {battery_pct:.1f} %")
    print(f"Gain tracker        : {tracker_gain:.1f} %")
    print(f"Peak detected       : {peak}")
    print(f"État numérique      : {state_code} = {state_label}")

    if peak == 1:
        print("Diagnostic          : PEAK DEMAND détecté")
    elif solar_power >= load_power:
        print("Diagnostic          : production suffisante")
    else:
        print("Diagnostic          : déficit compensé par batterie/réseau")

    if battery_pct < 20:
        print("Alerte              : batterie faible")

    print("---------------------------------------------\n")


# ==========================================================
# Boucle principale
# ==========================================================

def main():
    global panel_angle, battery_wh

    step = 0

    client = create_mqtt_client()
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    print("Simulation MQTT ThingSpeak démarrée. Ctrl+C pour arrêter.")
    print(f"Topic MQTT : {MQTT_TOPIC}")
    print(f"CSV local  : {CSV_FILE.resolve()}")

    try:
        while True:
            now = datetime.now()

            irradiance, temperature, load_power, sun_angle, weather = simulate_environment(step)

            panel_angle = update_tracker(panel_angle, sun_angle)

            power_tracker = compute_solar_power(
                irradiance=irradiance,
                temperature=temperature,
                panel_angle_value=panel_angle,
                sun_angle=sun_angle
            )

            power_fixed = compute_solar_power(
                irradiance=irradiance,
                temperature=temperature,
                panel_angle_value=FIXED_PANEL_ANGLE,
                sun_angle=sun_angle
            )

            tracker_gain_pct = compute_tracker_gain(power_tracker, power_fixed)

            battery_wh, battery_pct, grid_power, state = manage_energy(
                production_w=power_tracker,
                load_w=load_power,
                current_battery_wh=battery_wh
            )

            peak = detect_peak(load_power, power_tracker, battery_pct)

            alerts = generate_alerts(
                solar_power=power_tracker,
                load_power=load_power,
                battery_pct=battery_pct,
                grid_power=grid_power,
                weather=weather
            )

            state_code = encode_state(
                state=state,
                peak=peak,
                battery_pct=battery_pct,
                solar_power=power_tracker
            )

            tracking_error = abs(panel_angle - sun_angle)

            status = (
                f"{state}|weather={weather}|"
                f"alerts={','.join(alerts) if alerts else 'NONE'}"
            )

            data = {
                "timestamp": now.isoformat(timespec="seconds"),
                "step": step,
                "weather": weather,
                "irradiance": irradiance,
                "temperature": temperature,
                "sun_angle": sun_angle,
                "panel_angle": panel_angle,
                "tracking_error": tracking_error,
                "power_tracker": power_tracker,
                "power_fixed": power_fixed,
                "tracker_gain_pct": tracker_gain_pct,
                "load_power": load_power,
                "battery_wh": battery_wh,
                "battery_pct": battery_pct,
                "grid_power": grid_power,
                "state": state,
                "state_code": state_code,
                "peak": peak,
                "alerts": ",".join(alerts) if alerts else "NONE",
                "status": status
            }

            result, payload = publish_to_thingspeak_mqtt(client, data)
            save_to_csv(data)

            print("=" * 90)
            print(f"Time              : {data['timestamp']}")
            print(f"Weather           : {weather}")
            print(f"Irradiance        : {irradiance:.1f} W/m²")
            print(f"Temperature       : {temperature:.1f} °C")
            print(f"Solar tracker     : {power_tracker:.1f} W")
            print(f"Solar fixed       : {power_fixed:.1f} W")
            print(f"Tracker gain      : {tracker_gain_pct:.1f} %")
            print(f"Load demand       : {load_power:.1f} W")
            print(f"Battery           : {battery_pct:.1f} %")
            print(f"Grid power        : {grid_power:.1f} W")
            print(f"State             : {state} | code={state_code}")
            print(f"Peak              : {peak}")
            print(f"Alerts            : {', '.join(alerts) if alerts else 'NONE'}")
            print(f"MQTT payload      : {payload}")

            # Lecture/analyse périodique de ThingSpeak
            if step % 5 == 0:
                last_data = read_last_from_thingspeak()
                analyze_last_data(last_data)

            step += 1
            time.sleep(INTERVAL_S)

    except KeyboardInterrupt:
        print("\nArrêt de la simulation.")

    finally:
        client.loop_stop()
        client.disconnect()
        print("Client MQTT déconnecté.")


if __name__ == "__main__":
    main()