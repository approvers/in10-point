class In10Info:
    def __init__(self, user_id: int, name: str, point: int, count: int):
        self.user_id = user_id
        self.name = name
        self.point = point
        self.count = count

    def __str__(self):
        return f"[In10Point: {self.user_id}({self.name}) = {self.point}, {self.count}time(s)]"

    @classmethod
    def from_dict(cls, id, dict):
        return In10Info(id, dict["name"], dict["point"], dict["count"])

    def to_dict(self):
        return {
            "name": self.name,
            "point": self.point,
            "count": self.count
        }
