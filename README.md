# Simulation IoT d'un Système Photovoltaïque avec ThingSpeak MQTT

Ce projet est une simulation IoT appliquée aux énergies renouvelables.  
Il simule un système photovoltaïque avec tracker solaire, batterie, demande énergétique variable, détection de peak demand, alertes et publication des données vers ThingSpeak en utilisant le protocole MQTT.

Le projet est utile pour illustrer le rôle de l'IoT dans le monitoring énergétique, les smart grids, les systèmes cyber-physiques connectés et la supervision des énergies renouvelables.

---

## 1. Objectif du projet

L'objectif principal est de simuler un système photovoltaïque intelligent capable de :

- générer des données environnementales simulées ;
- calculer la production d'un panneau solaire avec tracker ;
- comparer un panneau solaire mobile avec un panneau fixe ;
- simuler la demande énergétique d'une charge ;
- gérer l'énergie entre production PV, batterie et réseau ;
- détecter les pics de demande énergétique ;
- générer des alertes ;
- publier les données vers ThingSpeak avec MQTT ;
- lire la dernière donnée depuis ThingSpeak ;
- sauvegarder les résultats localement dans un fichier CSV.

---

## 2. Fonctionnalités principales

Le programme permet de réaliser les fonctions suivantes :

- simulation de l'irradiance solaire ;
- simulation de la température ;
- simulation de plusieurs conditions météo ;
- calcul de la puissance photovoltaïque ;
- suivi automatique de l'angle solaire par un tracker ;
- comparaison entre tracker solaire et panneau fixe ;
- calcul du gain du tracker ;
- gestion d'une batterie virtuelle ;
- simulation de l'import et de l'injection réseau ;
- détection du peak demand ;
- génération d'alertes ;
- publication MQTT vers ThingSpeak ;
- lecture de la dernière donnée publiée ;
- analyse simple de l'état du système ;
- sauvegarde dans `simulation_log.csv`.

---

## 3. Architecture générale du système

```text
Simulation Python
       |
       | Génération des données :
       | irradiance, température, météo, demande énergétique
       v
Modèle photovoltaïque
       |
       | Calcul production tracker + panneau fixe
       v
Gestion énergétique
       |
       | Batterie, import réseau, injection réseau
       v
Détection peak demand + alertes
       |
       v
Publication MQTT vers ThingSpeak
       |
       v
Dashboard ThingSpeak + sauvegarde CSV locale
```

---

## 4. Technologies utilisées

Le projet utilise :

- Python 3 ;
- ThingSpeak ;
- MQTT ;
- paho-mqtt ;
- requests ;
- python-dotenv ;
- CSV pour la sauvegarde locale.

---

## 5. Structure recommandée du projet

Avant de déposer le projet sur GitHub, il est recommandé d'organiser les fichiers comme suit :

```text
projet-iot-photovoltaique/
│
├── p3.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── simulation_log.csv
```

> Remarque : si votre fichier Python s'appelle encore `p3(3).py`, il est préférable de le renommer en `p3.py` avant de le publier sur GitHub.

---

## 6. Description des fichiers

| Fichier | Rôle |
|---|---|
| `p3.py` | Programme principal de simulation et de communication MQTT avec ThingSpeak |
| `requirements.txt` | Liste des bibliothèques Python nécessaires |
| `.env` | Fichier contenant les identifiants ThingSpeak |
| `.env.example` | Exemple de configuration sans vraies clés |
| `simulation_log.csv` | Fichier généré automatiquement contenant les résultats de simulation |
| `README.md` | Documentation du projet |

---

## 7. Installation du projet

### 7.1. Cloner le dépôt

```bash
git clone https://github.com/votre-nom-utilisateur/projet-iot-photovoltaique.git
cd projet-iot-photovoltaique
```

### 7.2. Créer un environnement virtuel

Sous Windows :

```bash
python -m venv venv
venv\Scripts\activate
```

Sous Linux ou macOS :

```bash
python3 -m venv venv
source venv/bin/activate
```

### 7.3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Le fichier `requirements.txt` doit contenir :

```txt
requests
paho-mqtt
python-dotenv
```

---

7.1 Sous Windows :

```bash
copy .env.example .env

## 8. Configuration de ThingSpeak

Avant d'exécuter le programme, il faut créer un canal ThingSpeak.

### 8.1. Créer un canal ThingSpeak

Sur ThingSpeak :

1. créer un nouveau channel ;
2. activer 8 champs ;
3. récupérer le Channel ID ;
4. récupérer les identifiants MQTT ;
5. récupérer la Read API Key si vous voulez lire les dernières données depuis ThingSpeak.

---

## 9. Configuration des champs ThingSpeak

Le programme utilise les champs suivants :

| Field ThingSpeak | Donnée envoyée |
|---|---|
| `field1` | Irradiance solaire en W/m² |
| `field2` | Température en °C |
| `field3` | Puissance du panneau avec tracker en W |
| `field4` | Demande énergétique en W |
| `field5` | Niveau de batterie en % |
| `field6` | Gain du tracker solaire en % |
| `field7` | Détection de peak demand : 0 ou 1 |
| `field8` | État numérique du système |

---

## 10. Configuration du fichier `.env`

Le programme utilise un fichier `.env` pour charger les paramètres sensibles.

Créer un fichier `.env` à la racine du projet :

```env
THINGSPEAK_CHANNEL_ID=your_channel_id

THINGSPEAK_MQTT_CLIENT_ID=your_mqtt_client_id
THINGSPEAK_MQTT_USERNAME=your_mqtt_username
THINGSPEAK_MQTT_PASSWORD=your_mqtt_password

THINGSPEAK_READ_API_KEY=your_read_api_key
```

### Important

Le fichier `.env` ne doit pas être publié sur GitHub, car il contient des informations sensibles.

Il faut créer un fichier `.env.example` pour montrer la structure attendue sans partager les vraies clés.

Exemple de `.env.example` :

```env
THINGSPEAK_CHANNEL_ID=your_channel_id

THINGSPEAK_MQTT_CLIENT_ID=your_mqtt_client_id
THINGSPEAK_MQTT_USERNAME=your_mqtt_username
THINGSPEAK_MQTT_PASSWORD=your_mqtt_password

THINGSPEAK_READ_API_KEY=your_read_api_key
```

---

## 11. Fichier `.gitignore` recommandé

Créer un fichier `.gitignore` pour éviter d'envoyer les fichiers sensibles ou inutiles sur GitHub :

```gitignore
.env
venv/
__pycache__/
*.pyc
simulation_log.csv
```

Si vous voulez garder un exemple de résultats dans GitHub, vous pouvez publier un petit fichier CSV anonymisé, par exemple :

```text
simulation_log_example.csv
```

---

## 12. Exécution du programme

Pour lancer la simulation :

```bash
python p3.py
```

Le programme démarre une boucle continue.  
Chaque itération :

1. simule l'environnement ;
2. calcule la production solaire ;
3. gère la batterie ;
4. détecte les peaks ;
5. publie les données vers ThingSpeak ;
6. sauvegarde les données dans le fichier CSV.

Pour arrêter le programme :

```text
Ctrl + C
```

---

## 13. Fonctionnement détaillé

### 13.1. Simulation météo

Le programme simule plusieurs états météo :

```text
SUNNY
CLOUDY
STORM
PARTIAL_SHADING
```

Ces scénarios influencent l'irradiance solaire.

---

### 13.2. Simulation de l'environnement

À chaque étape, le programme génère :

- l'irradiance solaire ;
- la température ;
- la demande énergétique ;
- l'angle du soleil ;
- le scénario météo.

Le cycle de simulation représente une journée accélérée.

---

### 13.3. Modèle photovoltaïque

La puissance solaire est calculée selon :

- la surface du panneau ;
- le rendement du panneau ;
- l'irradiance ;
- la température ;
- l'angle entre le panneau et le soleil.

Le tracker solaire ajuste progressivement l'angle du panneau pour suivre le soleil.

---

### 13.4. Comparaison tracker solaire / panneau fixe

Le projet compare deux configurations :

```text
Panneau avec tracker solaire
Panneau fixe
```

Le gain du tracker est calculé avec la formule :

```text
gain = ((puissance_tracker - puissance_fixe) / puissance_fixe) × 100
```

---

### 13.5. Gestion de la batterie et du réseau

Le programme gère l'énergie selon deux cas.

#### Cas 1 : production supérieure à la demande

```text
Production PV > Demande
```

Le surplus est utilisé pour charger la batterie.  
Si la batterie est pleine, le surplus est injecté vers le réseau.

#### Cas 2 : production inférieure à la demande

```text
Production PV < Demande
```

La batterie fournit l'énergie manquante.  
Si la batterie ne suffit pas, le système importe de l'énergie depuis le réseau.

---

## 14. Détection du peak demand

Le peak demand est détecté lorsque la demande dépasse fortement la production solaire.

Le programme considère un peak lorsque :

```text
déficit énergétique important
```

ou lorsque :

```text
demande élevée + batterie faible ou moyenne
```

Le résultat est envoyé dans `field7` :

| Valeur | Signification |
|---|---|
| 0 | Pas de peak |
| 1 | Peak demand détecté |

---

## 15. États numériques du système

Les états du système sont convertis en codes numériques pour faciliter l'affichage sur ThingSpeak.

| Code | État |
|---|---|
| 0 | AUTONOME |
| 1 | CHARGE_BATTERIE |
| 2 | APPORT_BATTERIE |
| 3 | IMPORT_RESEAU |
| 4 | INJECTION_RESEAU |
| 5 | PEAK_DEMAND |
| 6 | BATTERIE_FAIBLE |
| 7 | FAIBLE_PRODUCTION |

---

## 16. Alertes générées

Le programme peut générer plusieurs alertes :

| Alerte | Signification |
|---|---|
| `BATTERIE_FAIBLE` | La batterie est inférieure à 20 % |
| `PEAK_DEMAND` | La demande dépasse fortement la production |
| `IMPORT_RESEAU_ELEVE` | L'import depuis le réseau est important |
| `FAIBLE_PRODUCTION_PV` | La production photovoltaïque est très faible |
| `METEO_STORM` | Condition météo orageuse |
| `METEO_PARTIAL_SHADING` | Ombrage partiel détecté |

---

## 17. Exemple de payload MQTT

Le programme envoie vers ThingSpeak un payload de ce type :

```text
field1=850.2&field2=31.5&field3=245.8&field4=180.4&field5=65.2&field6=12.3&field7=0&field8=1&status=CHARGE_BATTERIE|weather=SUNNY|alerts=NONE
```

---

## 18. Sauvegarde CSV

Les données sont sauvegardées automatiquement dans :

```text
simulation_log.csv
```

Le fichier contient notamment :

- timestamp ;
- step ;
- weather ;
- irradiance ;
- temperature ;
- sun_angle ;
- panel_angle ;
- tracking_error ;
- power_tracker ;
- power_fixed ;
- tracker_gain_pct ;
- load_power ;
- battery_wh ;
- battery_pct ;
- grid_power ;
- state ;
- state_code ;
- peak ;
- alerts ;
- status.

---

## 19. Lecture des données depuis ThingSpeak

Le programme lit périodiquement la dernière donnée publiée sur ThingSpeak grâce à l'API HTTP.

Cette partie permet d'afficher dans le terminal :

- l'irradiance ;
- la température ;
- la production tracker ;
- la demande énergétique ;
- le niveau de batterie ;
- le gain du tracker ;
- l'état numérique ;
- un diagnostic simple.

---

## 20. Exemple d'affichage dans le terminal

```text
Simulation MQTT ThingSpeak démarrée. Ctrl+C pour arrêter.
Topic MQTT : channels/CHANNEL_ID/publish
CSV local  : simulation_log.csv

Weather           : SUNNY
Irradiance        : 820.5 W/m²
Temperature       : 29.8 °C
Solar tracker     : 238.4 W
Solar fixed       : 210.7 W
Tracker gain      : 13.1 %
Load demand       : 175.6 W
Battery           : 63.5 %
Grid power        : 0.0 W
State             : CHARGE_BATTERIE
Peak              : 0
Alerts            : NONE
```

---

## 21. Interprétation IoT du projet

Ce projet représente un système IoT car :

- il génère ou collecte des données liées à un système physique ;
- il transmet ces données vers une plateforme cloud ;
- il utilise MQTT comme protocole de communication ;
- il permet la visualisation et l'analyse sur ThingSpeak.

Dans un cas réel, les données simulées pourraient être remplacées par des capteurs physiques connectés à une carte ESP32 ou Arduino.

---

## 22. Lien avec les systèmes cyber-physiques

Le projet peut aussi être interprété comme une base de système cyber-physique connecté, car il contient :

- une représentation du monde physique ;
- des données environnementales ;
- une logique de décision ;
- une gestion énergétique ;
- une détection d'état critique ;
- une interaction possible avec batterie et réseau.

Dans cette version, l'action est simulée.  
Avec des actionneurs réels, comme un relais, un convertisseur, une batterie réelle ou un contrôleur de charge, le système deviendrait un CPS IoT-enabled.

---

## 23. Limites du projet

Le projet reste une simulation.  
Il ne contient pas encore :

- de capteurs physiques réels ;
- de carte ESP32 ;
- de commande directe d'actionneurs ;
- de modèle de machine learning ;
- d'interface web locale ;
- de base de données externe.

---

## 24. Améliorations possibles

Plusieurs extensions sont possibles :

- ajouter une prédiction du peak demand avec machine learning ;
- connecter un ESP32 avec des capteurs réels ;
- utiliser ThingsBoard en plus de ThingSpeak ;
- ajouter FastAPI pour créer une interface web ;
- stocker les données dans MongoDB ;
- ajouter une stratégie intelligente de gestion de batterie ;
- créer un dashboard local avec Streamlit ;
- intégrer des données météo réelles ;
- ajouter une comparaison entre plusieurs sources renouvelables.

---

## 25. Commandes Git utiles

Initialiser un dépôt Git :

```bash
git init
git add .
git commit -m "Initial commit - IoT photovoltaic simulation"
```

Ajouter le dépôt distant :

```bash
git remote add origin https://github.com/votre-nom-utilisateur/projet-iot-photovoltaique.git
git branch -M main
git push -u origin main
```

---

## 26. Remarque de sécurité

Ne jamais publier les vraies clés API ou les identifiants MQTT dans GitHub.

Avant de publier le projet :

1. vérifier que `.env` est bien dans `.gitignore` ;
2. supprimer le fichier `.env` de Git si vous l'avez déjà ajouté ;
3. publier seulement `.env.example` ;
4. régénérer les clés ThingSpeak si elles ont déjà été partagées publiquement.

---

## 27. Auteur

Projet réalisé dans le cadre d'une étude sur l'Internet des Objets appliqué aux énergies renouvelables, au monitoring énergétique et aux smart grids.

---

## 28. Licence

Ce projet est destiné à un usage pédagogique, expérimental et académique.
