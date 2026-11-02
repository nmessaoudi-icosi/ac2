import time
import hashlib
import hmac

MAX_ATTEMPTS = 3
LOCK_TIME = 60  # secondes

# Compte de démonstration
USERNAME = "student"

# Mot de passe de démonstration : Secure@123
PASSWORD_HASH = hashlib.sha256("Secure@123".encode()).hexdigest()

failed_attempts = 0
locked_until = 0


def authenticate(username, password):
    global failed_attempts, locked_until

    current_time = time.time()

    # Vérifier si le compte est verrouillé
    if current_time < locked_until:
        remaining = int(locked_until - current_time)
        return False, f"Compte verrouillé. Réessayez dans {remaining} secondes."

    entered_hash = hashlib.sha256(password.encode()).hexdigest()

    valid_user = username == USERNAME
    valid_password = hmac.compare_digest(
        entered_hash,
        PASSWORD_HASH
    )

    if valid_user and valid_password:
        failed_attempts = 0
        return True, "Authentification réussie."

    failed_attempts += 1

    if failed_attempts >= MAX_ATTEMPTS:
        locked_until = time.time() + LOCK_TIME
        failed_attempts = 0
        return False, "Trop de tentatives. Compte verrouillé pendant 60 secondes."

    return False, f"Identifiants incorrects. Tentative {failed_attempts}/{MAX_ATTEMPTS}."


if __name__ == "__main__":
    user = input("Utilisateur : ")
    password = input("Mot de passe : ")

    success, message = authenticate(user, password)
    print(message)