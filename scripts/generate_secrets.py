#!/usr/bin/env python3
"""
Génère des clés secrètes et mots de passe sécurisés pour le projet FPP.
Les clés sont compatibles Docker Compose / .env (pas de $, !, `, {, }, etc.)

Usage :
    python scripts/generate_secrets.py
    python scripts/generate_secrets.py --key-only
    python scripts/generate_secrets.py --password-only
    python scripts/generate_secrets.py --length 64
"""

import argparse
import secrets
import string

SAFE_PUNCTUATION = "-_=+.^*"


def generate_django_secret_key(length=50):
    """Génère une SECRET_KEY compatible Django ET Docker Compose."""
    chars = string.ascii_letters + string.digits + SAFE_PUNCTUATION
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_password(length=32):
    """Génère un mot de passe alphanumérique sécurisé."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def main():
    parser = argparse.ArgumentParser(description="Générateur de secrets FPP")
    parser.add_argument("--key-only", action="store_true", help="Affiche uniquement une DJANGO_SECRET_KEY")
    parser.add_argument("--password-only", action="store_true", help="Affiche uniquement un mot de passe DB")
    parser.add_argument("--length", type=int, default=None, help="Longueur personnalisée")
    args = parser.parse_args()

    if args.key_only:
        print(generate_django_secret_key(args.length or 50))
    elif args.password_only:
        print(generate_password(args.length or 32))
    else:
        print("DJANGO_SECRET_KEY=" + generate_django_secret_key(args.length or 50))
        print("POSTGRES_PASSWORD=" + generate_password(args.length or 32))


if __name__ == "__main__":
    main()
