class In10Info:
    def __init__(self, user_id: int, point: int, count: int):
        self.user_id = user_id
        self.point = point
        self.count = count

    def __str__(self):
        return f"[In10Point: {self.user_id} = {self.point}, {self.count}time(s)]"

    @classmethod
    def from_dict(cls, id, dict):
        return In10Info(id, dict["point"], dict["count"])

    def to_dict(self):
        return {
            "point": self.point,
            "count": self.count
        }
