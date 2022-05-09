---
layout: default
title: Data
nav_order: 3
description: ""
permalink: /6ds/data
parent: 6Ds
---

# Data

## Training Data

This system is based on the inference of data moreso than training of models on data. The training data came from the same domain as that of the test data: Twitter. For sentiment analysis, a pre-trained model was used from [HuggingFace](https://huggingface.co/), a machine learning data and model hub for AI researchers and practitioners. [This particular model](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) was based on the [work](https://arxiv.org/pdf/2202.03829.pdf) of researchers from Cardiff University Natural Language Processing group. In their paper, *TimeLMs: Diachronic Language Models from Twitter*, authors explored language model degradation and language shifting via social media analysis. This model that resulted from this work is a transformer model based on the Bidirectional Encoder Representations from Transformers (BERT) model from [Google](https://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html). It was trained on a large corpus of 124+ million Tweets from January 2018 to December 2018 and fine-tuned for the task of sentiment analysis.

This Tweet corpus is a recent development, so training data is likely close to the distribution of current Tweets. Further, the model was designed from exploration of language shifting, so it is designed with time and change in mind. This is perfect for the application of Heartbeat since its modus operandi is the analysis of Tweet data over time.

Since this is a pre-trained model, there was fortunately no need to store or handle a 124M Tweet corpus.

## Inference Data

Data for inference comes from Twitter itself via the [filtered stream endpoint](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction), accessible via `POST /2/tweets/search/stream`. Rules can be set for filtering this stream via the [stream rules endpoint](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules), and such rules were created to target any content containing "Russia" or "Ukraine". This is a broad search, but initial exploration showed mentions of these counties on Twitter were nearly always pertaining to the current conflict.

To access this data, a [Twitter developer account](https://developer.twitter.com/en) was made, and a request was made to extend the account to have [Elevated access](https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api#v2-access-level) for access to 2M Tweets per month instead of the standard 500K.

There is a lot of data available for Tweets, but the only parts used in this system are the text content of the Tweets, their IDs for later reference, and their `created_at` timestamp. These 3 attributes can cover everything the system requires.

Tweet content is small but can accumulate given enough scale, so consideration was made into what data remains stored. In the processing of the data, actual text is discarded and only sentiment values were stored. This enabled storage of many tweets on my humble local system.
