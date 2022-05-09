---
layout: default
title: Design
nav_order: 4
description: ""
permalink: /6ds/design
parent: 6Ds
---

## Design

Thanks to the efforts of [HuggingFace](https://huggingface.co/) developers and model [authors](https://github.com/cardiffnlp), design was a light aspect in the creation of this system. Much of the work was done already in terms of the model itself: a large dataset was created and used to train a BERT transformer-based model. This model was fine-tuned for the task of sentiment analysis of Tweet text content using the [TweetEval benchmark](https://arxiv.org/pdf/2010.12421.pdf). TweetEval is a multi-task classification benchmark aimed at generating a standardized evaluation protocol for language models across seven different Twitter-specific classification tasks.

Using the [pre-trained model](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) and HuggingFace's transformer pipeline, sentiment analysis was very easy to incorporate into the overall system. Then, this system became a more of a data management problem where streaming data is constantly moving between services in high volumes.

Before being fed into the sentiment analysis model, data is converted to tokens via the transformer model. This means not much preprocessing was done, I needed to preserve as much context in the text as possible. Only URLs and Twitter handles were processed out of the text and standardized.


### Code

Code used for running sentiment analysis in the Heartbeat system is copied below. This code can also be found [here](https://github.com/jklasa/heartbeat/blob/main/src/analyze/sentiment_analyzer.py) in the GitHub repo.

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
