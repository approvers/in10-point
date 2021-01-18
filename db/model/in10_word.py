class In10Word:
    def __init__(self, word: str, weight: float):
        self.word = word
        self.raw_weight = weight
        self.weight = weight if weight > 0 else len(word) * 0.005

    @classmethod
    def from_tuple(cls, data: tuple):
        return In10Word(data[0], data[1])

    @classmethod
    def from_dict(cls, dict: dict):
        items = list(dict.items())
        words = list(map(lambda x: In10Word.from_tuple(x), items))
        return words

    def __str__(self):
        if self.raw_weight != self.weight:
            point = f"{self.raw_weight} => {self.weight}pt"
        else:
            point = f"{self.weight}pt"
        return f"[In10Word: '{self.word}' ({point})]"
