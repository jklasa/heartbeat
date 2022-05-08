from typing import List

from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax


class SentimentAnalyzer:
    def __init__(self):
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.config = AutoConfig.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name
        )

    def score(self, text: str) -> List[float]:
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
