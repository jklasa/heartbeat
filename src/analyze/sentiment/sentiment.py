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
        schema_file = "./sentiment/sentiment.json"
        with open(schema_file) as f:
            schema_str = f.read()
        return schema_str
