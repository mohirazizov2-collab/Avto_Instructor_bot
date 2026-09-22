import json
import os

import firebase_admin
from firebase_admin import credentials, firestore


def get_firestore():
    if firebase_admin._apps:
        return firestore.client()

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    if service_account_json:
        try:
            service_account_info = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_info)

            firebase_admin.initialize_app(cred)

            return firestore.client()

        except Exception as e:
            raise RuntimeError(
                f"Firebase environment credential error: {e}"
            ) from e

    base_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
        )
    )

    key_path = os.path.join(
        base_dir,
        "firebase-service-account.json",
    )

    if not os.path.exists(key_path):
        raise FileNotFoundError(
            "Firebase credentials not found. "
            "Set FIREBASE_SERVICE_ACCOUNT_JSON "
            "or provide firebase-service-account.json."
        )

    try:
        cred = credentials.Certificate(key_path)

        firebase_admin.initialize_app(cred)

        return firestore.client()

    except Exception as e:
        raise RuntimeError(
            f"Firebase initialization error: {e}"
        ) from e
