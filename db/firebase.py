import json
import logging

import firebase_admin
from firebase_admin import credentials, db

from db.model.in10_word import In10Word

logger = logging.getLogger(__name__)


class FirebaseRealtimeDatabase:
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        if FirebaseRealtimeDatabase.__instance__ is not None:
            logger.warning("Tried to generate multiple FRD instance.")
        else:
            FirebaseRealtimeDatabase.__instance__ = super(FirebaseRealtimeDatabase, cls).__new__(cls)
        return FirebaseRealtimeDatabase.__instance__

    def __init__(self, firebase_credential: str):
        dict_credential = json.loads(firebase_credential.replace("\n", ""))
        credential = credentials.Certificate(dict_credential)
        firebase_admin.initialize_app(credential, {"databaseURL": "https://in10-point-database-default-rtdb.firebaseio.com/"})
        logger.info("Initialized Firebase Admin SDK.")

    def get_in10_words(self):
        dict_data = db.reference("/in10-dictory").get()
        return In10Word.from_dict(dict_data)

    def get_in10_point(self, id):
        pass

