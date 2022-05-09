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

A dashboard 

## Confluent for Kubernetes and Kafka

## Services

### Twitter Ingest

### Analysis

### Database Storage

## InfluxDB
