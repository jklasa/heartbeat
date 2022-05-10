---
layout: default
title: Deployment
nav_order: 6
description: ""
parent: 6Ds
permalink: /6ds/deployment
---

# Deployment

There are many working parts in this system, as it eventually became largely a system designed for handing the problem of streaming data. High volumes of data are coming in and must be dealt with efficiently in a scalable manner.

Notably, when run unfettered, the system was able to ingest, analyze, and store around 20k Tweets in less than 5 minutes. Of course, this was too fast for sustainable use as Twitter API Tweet caps would be overrun too quickly with such a pace.


## Kubernetes

From personal experience, containers are the way to go for deployment of programs in a manageable way. Especially for this system where there are many moving parts, containers are ideal as they allow smaller parts of the system to be neatly packaged independently and deployed and re-deployed as needed. For ease of use and effective, efficient container management, [Kubernetes](https://github.com/kubernetes/kubernetes) was used as the orchestration tool. Kubernetes allows for high levels of control over container deployment and resource management. This was particularly important for my underpowered local system machine that had limited resources to work with. Kubernetes also enabled easy networking between systems and scaling as well. In the running of this system, I found that the sentiment analysis service, which required more CPU time, was slower than the Tweet ingest service. To amend this, I was able to just scale up the number of analysis pods to 2 by just changing one line in the Kubernetes configuration.

Deployment was also made easier by adding in already-configured Helm charts for both Confluent and InfluxDB (to be discussed later). Helm charts are tools used for Kubernetes for template-based deployments.

A dashboard was run for the local Kubernetes cluster that made management of the great number of pods possible.

Kubernetes configuration files can be found in the GitHub repo [here](https://github.com/jklasa/heartbeat/tree/main/k8s).

## Confluent for Kubernetes and Kafka

A personal version of [Confluent](https://www.confluent.io/blog/confluent-for-kubernetes-offers-cloud-native-kafka-automation/) was run within Kubernetes. This part of the system added the messaging service Kafka and its components: ksqlDB, a SchemaRegistry service, Kafka brokers, a Confluent operator, and a Kafka rest proxy.

Kafka was the glue holding together all individual parts of the system via modeled messages.

## Services

There were 3 main processes happening in the system, detailed below. Each of these services has an associated Docker image and deployment running in Kubernetes.

### Twitter Ingest

Retrieve data from Twitter via a filtered stream and push each Tweet to Kafka. The filter is based on dynamic tasking: the system accepts search rules that can be used to filter Tweets and assign topic tags.

### Analysis

Retrieve Tweets from Kafka, run them through a sentiment analysis model, and push them back to Kafka with their sentiment results.

### Database Storage

Retrieve Tweets and their sentiments from Kafka and push them to final storage in time series database for aggregation and analysis.

## InfluxDB

For this project, I used [InfluxDB](https://github.com/influxdata/influxdb), an efficient time-series database for storing the sentiments according to the timestamps at which they were retrieved. The InfluxDB deployment I used also had readily-available dashboards for data visualization and analysis of the Twitter sentiment results.

