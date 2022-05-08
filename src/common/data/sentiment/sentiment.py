from common.adt import ADT


class Sentiment(ADT):
    def __init__(
        self, task: str, time: int, pos: float, neu: float, neg: float
    ):
        self.task = task
        self.time = time
        self.pos = pos
        self.neu = neu
        self.neg = neg

    @classmethod
    @property
    def schema(cls) -> str:
        schema_file = "./common/data/sentiment/sentiment.json"
        with open(schema_file) as f:
            schema_str = f.read()
        return schema_str

    def make_line(self, id_) -> str:
        return (
            f"{self.task} pos={self.pos},neu={self.neu},"
            f"neg={self.neg},tid={id_} {self.time}"
        )
