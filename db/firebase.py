import json
import logging
from typing import List, Optional

import firebase_admin
from firebase_admin import credentials, db

from db.model.in10_info import In10Info
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

    def get_in10_words(self) -> List[In10Word]:
        dict_data = db.reference("/in10-dictory").get()
        return In10Word.from_dict(dict_data)

    def get_user_in10_point(self, id) -> Optional[In10Info]:
        in10_data_ref = db.reference(f"/in10-points/{id}")
        if in10_data_ref.get() is None:
            return None

        in10_data = in10_data_ref.get()
        return In10Info.from_dict(id, in10_data)

    def get_all_in10_points(self) -> List[In10Info]:
        in10_data = db.reference(f"/in10-points").get()
        if in10_data is None:
            return []

        parsed_in10_info = list(map(lambda kv: In10Info.from_dict(kv[0], kv[1]), in10_data.items()))
        return parsed_in10_info

    def add_user_in10_point(self, id, name, point, count):
        in10_data_ref = db.reference(f"/in10-points/{id}")
        if in10_data_ref.get() is None:
            in10_data_ref.set(In10Info(id, name, 0, 0).to_dict())

        current_in10_point = self.get_user_in10_point(id)
        current_in10_point.count += count
        current_in10_point.point += point

        in10_data_ref.set(current_in10_point.to_dict())

