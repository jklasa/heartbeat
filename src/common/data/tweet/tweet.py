from common.adt import ADT


class Tweet(ADT):   
    def __init__(self, task: str, content: str, time: int):
        self.task = task
        self.content = content
        self.time = time
    
    @classmethod
    @property
    def schema(cls) -> str:
        schema_file = "./common/data/tweet/tweet.json"
        with open(schema_file) as f:
            schema_str = f.read()
        return schema_str
        
