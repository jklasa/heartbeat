---
layout: default
title: Demo
nav_order: 3
description: ""
permalink: /demo
---

# Heartbeat Demo
---

If you would like to run this notebook, this could be easily done on [Google Colab](https://colab.research.google.com/github/jklasa/heartbeat/blob/main/demo.ipynb).

This project serves as a way to measure the "heartbeat" of the Internet. In this case, the stethoscope is this AI-enabled system, and we are measuring the state via Twitter.

The system runs in a local Kubernetes (K8s) cluster, but can conceivably be pushed to the cloud with ease. Since running a somewhat intensive K8s cluster is not an easy task, I will demonstrate the main mechanics of the project in this walkthrough and mock the Kubernetes services.

Inside the K8s cluster is a Kafka service at the center of it all. This is also difficult to set up, so this will also be mocked here. I use mocking in this case to mean the environment will be simulated - the actual functions will not be mocked, but the behavior will be similar.

There are 3 main processes happening in this system, and we will cover all 3 in simple demonstrations in this notebook.

1. **Twitter ingest** - Retrieve data from Twitter via a filtered stream and push each Tweet to Kafka. The filter is based on dynamic tasking: the system accepts search rules that can be used to filter Tweets and assign topic tags.
2. **Sentiment analysis** - Retrieve Tweets from Kafka, run them through a sentiment analysis model, and push them back to Kafka with their sentiment results.
3. **Database storage** - Retrieve Tweets and their sentiments from Kafka and push them to final storage in time series database for aggregation and analysis.

Each of these services has an associated Docker image and deployment running in Kubernetes.

# Mocking Kafka

Kafka has a number of brokers that deal in messages based on topics. Producers and consumers can operate on these message streams by requesting or supplying data based on the desired topic.

Any data that enters Kafka is serialized by some method. In the real system, data is serialized by custom numeric serializers and an [Apache Avro](https://avro.apache.org/docs/current/spec.html) serializer. All tweet and sentiment data payloads sent via Kafka are stored as Avro data, which is a data serialization system for arbitrary data. To use it, I define schemas based on how the data is expected to present itself. 

These schemas are registered with a Kafka SchemaRegistry service running in the K8s cluster. Here, I will just convert to and from normal dictionaries.


```python
import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple, Union

from sty import fg, rs
```

Here, we start making the simulated environment for Kafka. This `KafkaStream` below represents a Kafka broker, where we can add (key, value) pairs of data to arbitrary topics and pull (key, value) pairs from those same topics as they are produced. The asynchronous behavior will be simulated with Python's threading module.


```python
class KafkaStream:
    def __init__(self):
        print(fg.cyan + "KAFKA " + rs.all, end="")
        print("Connected to new Kafka broker")
        self.data = defaultdict(list)
        self.lock = threading.Lock()

    # Add data to a topic
    def add(self, topic: str, key: int, value: dict) -> None:
        self.lock.acquire()
        print(fg.cyan + "KAFKA " + rs.all, end="")
        print(fg.magenta + f"{topic} " + rs.all, end="")
        print(fg.green + "ADD" + rs.all + f" {key} = {value}")
        self.data[topic].append((key, value))
        self.lock.release()
        time.sleep(0.1)

    # Get data from a topic, if there is any
    def get(self, topic) -> Tuple[int, str]:
        self.lock.acquire()
        print(fg.cyan + "KAFKA " + rs.all, end="")
        print(fg.magenta + f"{topic} " + rs.all, end="")
        if len(self.data[topic]) > 0:
            res = self.data[topic].pop(0)
            print(fg.red + "GET" + rs.all + f" {res[0]} = {res[1]}")
        else:
            res = None
            print(fg.red + "GET" + rs.all + " EMPTY")
        self.lock.release()
        time.sleep(0.1)
        return res 
```

Producers, as their name would suggest, produce data to given topics in Kafka. Consumers pull the data out of Kafka as it is produced by the producers. In the simulated environment and in the actual production environment, these producers and consumers interact with the Kafka broker through production and polling.

The interfaces shown below closely mirror their actual usage in the production environment.


```python
class KafkaProducer:
    def __init__(self, stream: KafkaStream, serialize: Callable):
        self.stream = stream
        self.serialize = serialize
        self.buffer = []
    
    def produce(self, topic, key, value) -> None:
        # Messages are buffered for more accurate simulation.
        # Use poll() to flush the buffer.
        self.buffer.append((topic, key, self.serialize(value, None)))
        
    def poll(self) -> int:
        size = len(self.buffer)
        for item in self.buffer:
            self.stream.add(*item)
        self.buffer = []
        return size
```


```python
class KafkaConsumer:
    def __init__(self, stream: KafkaStream, deserialize: Callable):
        self.stream = stream
        self.deserialize = deserialize
        self.topic = None
        
    def subscribe(self, topic) -> None:
        self.topic = topic
    
    def poll(self) -> Any:
        res = self.stream.get(self.topic)
        if res is None:
            return None
        key, value = res
        return key, self.deserialize(value, None)
```

# Framework

Here begins the design framework that I built for working with Kafka messages and my unique data needs.

Below is an abstract data type used to define some form of data used in the Heartbeat platform. This allowed me to very easily define data types that would be stored or moved in the form of Kafka messages. As mentioned before, I used Kafka in an entirely serialized fashion, so there had to be efficient methods for moving to and from serialized bytes and usable Python datatypes.


```python
from abc import ABC, abstractmethod


class ADT(ABC):
    def to_dict(self, ctx):
        return self.__dict__

    @classmethod
    def from_dict(cls, obj, ctx):
        if obj is None:
            return None
        return cls(**obj)

    @classmethod
    @property
    @abstractmethod
    def schema(cls) -> str:
        pass
```

I built my own custom Producer and Consumers on top of the library SerializedProducer and SerializedConsumer classes for ease of use.


```python
class Producer(KafkaProducer):
    def __init__(self, topic: str, data: ADT, stream: KafkaStream):
        self.topic = topic
        super().__init__(stream, data.to_dict)
        
    def produce(self, key: int, value: Any) -> None:
        super().produce(self.topic, key, value)
```


```python
class Consumer(KafkaConsumer):
    def __init__(self, data: ADT, stream: KafkaStream):
        super().__init__(stream, data.from_dict)
```

# 1. Twitter Ingest

## Twitter

```# import tweepy```

Here is a client that will produce random fake Tweet data for this demonstration. Access to the actual API requires authorization dependent on a user with an active account. I have an account with [Elevated](https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api#v2-access-level) access that I personally requested from Twitter, but I figured it would not be a good idea to publicly post the auth tokens on GitHub.

This begins the first step in the system: the ingest of content from Twitter. In this case, data comes from the Twitter filtered stream endpoint via `POST /2/tweets/search/stream`.


```python
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from threading import Thread

import requests
```


```python
@dataclass
class TweepyTweet:
    id: int
    text: str
    created_at: datetime
```

Tweet text content is just a random string of 15 words, so the sentiment results will not be useful, but the demonstrations will be perfectly workable.


```python
class TweepyClient(ABC):
    """ Mock tweepy.StreamingClient """
    
    def __init__(self):
        word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_site)
        self.vocab = [b.decode("utf-8") for b in response.content.splitlines()]

    def start(self, num: int = 100):
        t = Thread(target=self.generate, args=(num,))
        t.start()
        return t

    def generate(self, num: int):
        for i in range(num):
            tweet = TweepyTweet(
                id=random.randint(0, 10000),
                text=" ".join(random.sample(self.vocab, 15)),
                created_at=datetime.utcnow(),
            )
            self.on_tweet(tweet)

    @abstractmethod
    def on_tweet(self, tweet):
        pass
```

## Data

Data is represented using one of my abstract data types. I also define a schema for the Kafka SchemaRegistry service so that it can properly understand the incoming and outgoing data.

Twitter data only needs 3 attributes for representing Tweets:

* **task** - the Heartbeat tasking. This is the subject of the search. In our case, I was searching for Russia-Ukraine information.
* **content** - the text content of the Tweet.
* **time** - timestamp with only second precision. High precision is not really needed for this purpose.


```python
class Tweet(ADT):
    def __init__(self, task: str, content: str, time: int):
        self.task = task
        self.content = content
        self.time = time

    @classmethod
    @property
    def schema(cls) -> str:
        return """
        {
            "name": "tweet",
            "type": "record",
            "namespace": "heartbeat",
            "fields": [
                {
                    "name": "time",
                    "type": {
                        "type": "int", 
                        "logicalType": "timestamp-millis"
                    }
                },
                {"name": "content", "type": "string"},
                {"name": "task", "type": "string"}
            ]
        }
        """
```

## Tweepy - Kafka Interaction

With some of the mocking and setup out of the way, we can look at the services. The first part of the Heartbeat system involves ingesting the data from Twitter and producing it to the "ingest" topic in Kafka.

This simple service just connects to the Twitter stream endpoint, and as Tweets are received, pushes structured data to the topic. Data comes in from a Python wrapper for the Twitter API called `Tweepy`, which is mocked above. This library allowed for very simple access to the Twitter API: the work here was just a matter of connecting the stream of data coming from Twitter and Tweepy to Kafka.


```python
class TwitterIngest(TweepyClient):
    def __init__(self, task: str, producer: Producer):
        self.task = task
        self.producer = producer
        super().__init__()

    # This will get called when new Tweet data comes in
    def on_tweet(self, tweet):
        # Make a payload and send it to the Kafka producer
        payload = Tweet(self.task, tweet.text, tweet.created_at.timestamp())
        self.producer.produce(key=tweet.id, value=payload)

    def poll(self) -> None:
        # Pull Tweets until we run out
        empty = False
        while not empty:
            time.sleep(0.3)
            empty = self.producer.poll() == 0
        print(">>> Exiting Twitter ingest")
```

## Demo

Make a new Kafka service.


```python
stream = KafkaStream()
```

    [36mKAFKA [0mConnected to new Kafka broker


Make a producer for moving data into Kafka and a service that will pull from Twitter and send to Kafka via this producer.


```python
producer = Producer("ingest", Tweet, stream)
ingest = TwitterIngest("RU-UKR", producer)
```

Run the demo for a total of 5 Tweets. We should see 5 tweets get pushed to the Kafka topic "ingest".


```python
t = ingest.start(num=5)
ingest.poll()
```

    [36mKAFKA [0m[35mingest [0m[32mADD[0m 6863 = {'task': 'RU-UKR', 'content': 'featured hardly office turtle lonely expense pillow easily creating fully kijiji bankruptcy balanced despite name', 'time': 1652077269.927678}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 7655 = {'task': 'RU-UKR', 'content': 'crude widescreen personal movies compaq ntsc thursday forces museum african believed findlaw profits playback charleston', 'time': 1652077269.927722}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 8013 = {'task': 'RU-UKR', 'content': 'sc hardwood suddenly specs filter losses exact attractive sleep aud doug faith auburn gmc accordance', 'time': 1652077269.927738}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 2303 = {'task': 'RU-UKR', 'content': 'guard effectiveness campbell administration housing shaw republican ada satisfied hygiene center ridge motherboard engaging thou', 'time': 1652077269.927753}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 1315 = {'task': 'RU-UKR', 'content': 'constantly logs phones whereas summary disorders facility concern waterproof exam rand totally sigma dosage winner', 'time': 1652077269.927766}
    >>> Exiting Twitter ingest


So now we have an incoming stream of Tweets with a very simple data schema. Next, we just have to process this data for sentiment.

# 2. Sentiment Analysis

## Data

As before, there will be some more data structures to deal with. This time, we will be using data storage for sentiment analysis results. This can be thought of as the system's method of making data "models".

We are still storing the task information, but we are now also storing 3 different floating-point values for Tweet sentiments.

* **task** - the Heartbeat tasking. This is the subject of the search. In our case, I was searching for Russia-Ukraine information.
* **time** - timestamp with only second precision. High precision is not really needed for this purpose. Should still be the timestamp from Twitter, not one that we create.
* **pos** - likelihood of positive sentiment. Values range from 0 to 1 such that higher values indicate higher likelihood. Positive sentiment indicates favorable opinion of the tasking.
* **neu** - likelihood of neutral sentiment. Neutral sentiment indicates no particular positive or negative opinion.
* **neg** - likelihood of negative sentiment. Negative sentiment indicates some degree of dislike with the tasking.


```python
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
        return """
        {
            "name": "sentiment",
            "type": "record",
            "namespace": "heartbeat",
            "fields": [
                {
                    "name": "time",
                    "type": {"type": "int", "logicalType": "timestamp-millis"}
                },
                {"name": "task", "type": "string"},
                {"name": "pos", "type": "float"},
                {"name": "neu", "type": "float"},
                {"name": "neg", "type": "float"}
            ]
        }
        """
```

## Model Inference

We will use a pre-trained model from [HuggingFace](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) for running our sentiment analysis. This model is a transformer model based on the Bidirectional Encoder Representations from Transformers (BERT) model from [Google](https://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html). This version was trained on 124 million Tweets from January 2018 to December 2018 and fine-tuned for the task of sentiment analysis. The research behind this came from [TimeLMs: Diachronic Language Models from Twitter](https://arxiv.org/pdf/2202.03829.pdf), where authors explored language model degradation and language shifts via social media.

Tokenization will come from the transformer model, and only simple preprocessing will be done to handle links and usernames. The rest can be handled by the tokenizer itself since we do not want to lose any context that might be helpful for the transformer and the sentiment analysis model.


```python
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax


class SentimentAnalyzer:
    def __init__(self):
        # Load tokenizer, model, and config
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.config = AutoConfig.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name
        )

    def score(self, text: str) -> List[float]:
        # Assess sentiment of text
        processed = SentimentAnalyzer.preprocess(text)
        encoded_input = self.tokenizer(processed, return_tensors="pt")
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        return softmax(scores) # negative, neutral, positive

    @staticmethod
    def preprocess(text: str) -> str:
        # Preprocess text (username and link placeholders)
        new_text = []
        for t in text.split(" "):
            t = "@user" if t.startswith("@") and len(t) > 1 else t
            t = "http" if t.startswith("http") else t
            new_text.append(t)
        return " ".join(new_text)
```

    /home/jklasa/anaconda3/envs/hbtest/lib/python3.10/site-packages/tqdm/auto.py:22: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
      from .autonotebook import tqdm as notebook_tqdm


Below is a simple routine to analyze Tweets. We consume data from the Kafka topic "ingest", run model inference, and finally push the data to a different Kafka topic "sentiment".


```python
def analyze(stream, analyzer):
    consumer = Consumer(Tweet, stream)
    consumer.subscribe("ingest")
    producer = Producer("sentiment", Sentiment, stream)

    empty = 0
    while empty < 5:
        msg = consumer.poll()
        if msg is None:
            empty += 1
            continue

        key, tweet = msg
        if tweet is not None:
            negative, neutral, positive = analyzer.score(tweet.content)
            sentiment = Sentiment(
                task=tweet.task,
                time=tweet.time,
                pos=positive,
                neu=neutral,
                neg=negative,
            )
            producer.produce(key=key, value=sentiment)
        producer.poll()
    print(">>> Exiting sentiment analysis")
```

## Demo

Let's see how some of this would work. First, we just have to load the model from HuggingFace, where pretrained models are made extremely accessible for users.


```python
# Set up sentiment analysis
analyzer = SentimentAnalyzer()
```

    Some weights of the model checkpoint at cardiffnlp/twitter-roberta-base-sentiment-latest were not used when initializing RobertaForSequenceClassification: ['roberta.pooler.dense.weight', 'roberta.pooler.dense.bias']
    - This IS expected if you are initializing RobertaForSequenceClassification from the checkpoint of a model trained on another task or with another architecture (e.g. initializing a BertForSequenceClassification model from a BertForPreTraining model).
    - This IS NOT expected if you are initializing RobertaForSequenceClassification from the checkpoint of a model that you expect to be exactly identical (initializing a BertForSequenceClassification model from a BertForSequenceClassification model).


With the models loaded, we can determine sentiment from the text. Note that the return order from the model is [negative, neutral, positive].


```python
analyzer.score("We are absolutely loving this!")
```




    array([0.00420294, 0.00935337, 0.98644376], dtype=float32)




```python
analyzer.score("This is terrible")
```




    array([0.8545521 , 0.11869626, 0.02675165], dtype=float32)




```python
analyzer.score("HuggingFace is a machine learning library")
```




    array([0.02685222, 0.7657344 , 0.20741342], dtype=float32)



Looking at the sentiment results, we can see they make sense: the first example is positive, the second one is negative, and the third one is neutral.

We can even attach this analyzer to the Tweet data. The text is random gibberish, so the sentiment outputs are not very useful, but the system can still be demonstrated in this manner.


```python
class DemoAnalyzer(TweepyClient):
    def __init__(self, analyzer, *args, **kwargs):
        self.analyzer = analyzer
        super().__init__(*args, **kwargs)

    def on_tweet(self, tweet):
        # Called when new Tweets come in
        print(f"> TEXT: {tweet.text}")
        pos, neu, neg = self.analyzer.score(tweet.text)
        print(f"  SENTIMENT: pos={pos:.3f}, neu={neu:.3f}, neg={neg:.3f}")
```


```python
da = DemoAnalyzer(analyzer)
```


```python
y = da.start(5)
y.join()
```

    > TEXT: merger issued listings believe palm eagle cayman ringtones posters britannica traditions laws witness exams league
      SENTIMENT: pos=0.020, neu=0.930, neg=0.050
    > TEXT: hell faced deluxe src revolutionary infection small georgia functional sn withdrawal satisfactory particularly macedonia pichunter
      SENTIMENT: pos=0.164, neu=0.735, neg=0.101
    > TEXT: wearing partnerships em pop approaches improvement custom eleven concluded stay eva harvard jr lips ws
      SENTIMENT: pos=0.011, neu=0.936, neg=0.053
    > TEXT: epinionscom au petition forecasts ol bond climb chan hayes worry fd maria registrar mass pod
      SENTIMENT: pos=0.081, neu=0.868, neg=0.051
    > TEXT: astronomy particles responsibility bargains interests cam southeast punch bugs showers breaks specify convinced machines retired
      SENTIMENT: pos=0.141, neu=0.824, neg=0.035


# 3. Database Storage

The last step is transfer of the results from Kafka to a database for storage. For this project, I used [InfluxDB](https://github.com/influxdata/influxdb), an efficient time-series database for storing the sentiments according to the timestamps at which they were retrieved. This will again be mocked with a simple write and get_all interface.


```python
class Database:
    def __init__(self, lock):
        self.data = []
        self.lock = lock
        
    def write(self, item):
        self.lock.acquire()
        print(fg.grey + "DB " + rs.all, end="")
        print(fg.green + "ADD" + rs.all + f" {item}")
        
        self.lock.release()
        self.data.append(item)
        
    def get_all(self):
        print("Database dump...")
        for idx, item in enumerate(self.data):
            print(f"{idx}) {item}")
```

Below is a routine to consume data from Kafka topic "sentiment" and push to the database for the final destination.


```python
def transfer(stream: KafkaStream, db: Database, size: int):
    consumer = Consumer(Sentiment, stream)
    consumer.subscribe("sentiment")

    count = 0
    while count < size:
        msg = consumer.poll()
        if msg is None:
            continue

        count += 1
        key, sent = msg
        db.write([key, sent.task, sent.time, sent.pos, sent.neu, sent.neg])
    print(">>> Exiting data storage")
```

# Full Demo

Now let's put it all together and let the ingest service retrieve data from "Twitter" and push it to "Kafka". Meanwhile, we will let the analyzer service retrieve data from "Kafka" and produce sentiment analysis results. Finally, these results will be pushed to our database.


```python
# Set up the stream
stream = KafkaStream()

# Set up the database
db = Database(stream.lock)

# 1. Twitter Ingest
producer = Producer("ingest", Tweet, stream)
ingest = TwitterIngest("RU-UKR", producer)
t1 = ingest.start(5)
t2 = Thread(target=ingest.poll())

# 2. Sentiment Analysis
t3 = Thread(target=analyze, args=(stream, analyzer))

# 3. Database Storage
t4 = Thread(target=transfer, args=(stream, db, 5))

threads = [t1, t2, t3, t4]
for t in threads[1:]:
    t.start()
for t in threads:
    t.join()
```

    [36mKAFKA [0mConnected to new Kafka broker
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 451 = {'task': 'RU-UKR', 'content': 'israel something aware nano drop imagination synthetic wireless kay cartridges few engage industry gathered war', 'time': 1652077277.386532}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 1049 = {'task': 'RU-UKR', 'content': 'herbal tool reflect collapse interpretation looks tables burton bean mitsubishi frozen wars belfast cohen assistant', 'time': 1652077277.386616}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 6458 = {'task': 'RU-UKR', 'content': 'improvement expense shoes formal specific summer love save samba carroll algorithms diseases hungarian date registry', 'time': 1652077277.386634}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 6163 = {'task': 'RU-UKR', 'content': 'raleigh flooring leaf pdas johnston showed ecology aspect elimination class res ultra eight releases of', 'time': 1652077277.38666}
    [36mKAFKA [0m[35mingest [0m[32mADD[0m 2627 = {'task': 'RU-UKR', 'content': 'pro revision job testimony interior experiments consent swedish afghanistan diego format polished revelation grand on', 'time': 1652077277.386681}
    >>> Exiting Twitter ingest
    [36mKAFKA [0m[35mingest [0m[31mGET[0m 451 = {'task': 'RU-UKR', 'content': 'israel something aware nano drop imagination synthetic wireless kay cartridges few engage industry gathered war', 'time': 1652077277.386532}
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[32mADD[0m 451 = {'task': 'RU-UKR', 'time': 1652077277.386532, 'pos': 0.0462605, 'neu': 0.81405675, 'neg': 0.13968267}
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m 451 = {'task': 'RU-UKR', 'time': 1652077277.386532, 'pos': 0.0462605, 'neu': 0.81405675, 'neg': 0.13968267}
    [36mKAFKA [0m[35mingest [0m[31mGET[0m 1049 = {'task': 'RU-UKR', 'content': 'herbal tool reflect collapse interpretation looks tables burton bean mitsubishi frozen wars belfast cohen assistant', 'time': 1652077277.386616}
    [38;5;249mDB [0m[32mADD[0m [451, 'RU-UKR', 1652077277.386532, 0.0462605, 0.81405675, 0.13968267]
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[32mADD[0m 1049 = {'task': 'RU-UKR', 'time': 1652077277.386616, 'pos': 0.03076393, 'neu': 0.8217568, 'neg': 0.1474793}
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m 1049 = {'task': 'RU-UKR', 'time': 1652077277.386616, 'pos': 0.03076393, 'neu': 0.8217568, 'neg': 0.1474793}
    [36mKAFKA [0m[35mingest [0m[31mGET[0m 6458 = {'task': 'RU-UKR', 'content': 'improvement expense shoes formal specific summer love save samba carroll algorithms diseases hungarian date registry', 'time': 1652077277.386634}
    [38;5;249mDB [0m[32mADD[0m [1049, 'RU-UKR', 1652077277.386616, 0.03076393, 0.8217568, 0.1474793]
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[32mADD[0m 6458 = {'task': 'RU-UKR', 'time': 1652077277.386634, 'pos': 0.06477577, 'neu': 0.8149433, 'neg': 0.120280795}
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m 6458 = {'task': 'RU-UKR', 'time': 1652077277.386634, 'pos': 0.06477577, 'neu': 0.8149433, 'neg': 0.120280795}
    [36mKAFKA [0m[35mingest [0m[31mGET[0m 6163 = {'task': 'RU-UKR', 'content': 'raleigh flooring leaf pdas johnston showed ecology aspect elimination class res ultra eight releases of', 'time': 1652077277.38666}
    [38;5;249mDB [0m[32mADD[0m [6458, 'RU-UKR', 1652077277.386634, 0.06477577, 0.8149433, 0.120280795]
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[32mADD[0m 6163 = {'task': 'RU-UKR', 'time': 1652077277.38666, 'pos': 0.04155181, 'neu': 0.9429347, 'neg': 0.015513566}
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m 6163 = {'task': 'RU-UKR', 'time': 1652077277.38666, 'pos': 0.04155181, 'neu': 0.9429347, 'neg': 0.015513566}
    [36mKAFKA [0m[35mingest [0m[31mGET[0m 2627 = {'task': 'RU-UKR', 'content': 'pro revision job testimony interior experiments consent swedish afghanistan diego format polished revelation grand on', 'time': 1652077277.386681}
    [38;5;249mDB [0m[32mADD[0m [6163, 'RU-UKR', 1652077277.38666, 0.04155181, 0.9429347, 0.015513566]
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35msentiment [0m[32mADD[0m 2627 = {'task': 'RU-UKR', 'time': 1652077277.386681, 'pos': 0.12736656, 'neu': 0.8120202, 'neg': 0.060613222}
    [36mKAFKA [0m[35msentiment [0m[31mGET[0m 2627 = {'task': 'RU-UKR', 'time': 1652077277.386681, 'pos': 0.12736656, 'neu': 0.8120202, 'neg': 0.060613222}
    [36mKAFKA [0m[35mingest [0m[31mGET[0m EMPTY
    [38;5;249mDB [0m[32mADD[0m [2627, 'RU-UKR', 1652077277.386681, 0.12736656, 0.8120202, 0.060613222]
    >>> Exiting data storage
    [36mKAFKA [0m[35mingest [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35mingest [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35mingest [0m[31mGET[0m EMPTY
    [36mKAFKA [0m[35mingest [0m[31mGET[0m EMPTY
    >>> Exiting sentiment analysis


And then, of course, we can get the results in the database and easily inspect them. InfluxDB makes this very easy as well, as it has built-in dashboards for visualization of time series data.


```python
db.get_all()
```

    Database dump...
    0) [451, 'RU-UKR', 1652077277.386532, 0.0462605, 0.81405675, 0.13968267]
    1) [1049, 'RU-UKR', 1652077277.386616, 0.03076393, 0.8217568, 0.1474793]
    2) [6458, 'RU-UKR', 1652077277.386634, 0.06477577, 0.8149433, 0.120280795]
    3) [6163, 'RU-UKR', 1652077277.38666, 0.04155181, 0.9429347, 0.015513566]
    4) [2627, 'RU-UKR', 1652077277.386681, 0.12736656, 0.8120202, 0.060613222]



```python

```
