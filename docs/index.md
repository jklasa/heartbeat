---
layout: default
title: Decomposition
nav_order: 1
description: ""
permalink: /
---

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# The Problem

The impact of social media is an incredibly important topic in society today. Social media sites have power for both good and bad (subject to personal opinion, of course), and every minute, an incredible amount of information is posted and shared among millions of users. That volume of data can have significant value, but how can it be analyzed, and what type of knowledge can be gained from studying it?

# The Solution: Heartbeat

Here, I propose a system whose goal will be to achieve new insight into social media trends using current and historic social media data. It will look for ways to measure social media opinion and influence via the analysis of public data. To divide this problem into a practical independent task, the analysis will focus on Twitter data, which takes the form of short, 280-character posts. Using such a system, I hope to put a metaphorical stethoscope on the heartbeat of the Internet.
As a proof of concept for the utility of such a service, I will focus on conducting sentiment analysis on domain-specific data. As I mentioned, social media sites have the power for both good and bad. Some of this is known by general users and some is not, and there are many difficult tasks and decisions social media companies and users are faced with. How do we combat disinformation campaigns? Illegal content? Where is the line drawn between free speech and the common good? There is a lot to deal with here, but one place to start with is metrics: analyzing the data and finding out what is actually out there.

# Components

## Project Documentation

This site hosts the documentation for the project and the underlying system. Explore the navigation links on the left to browse the project as they pertain to the 6Ds of creating AI-enabled systems.
 
## GitHub

The [GitHub page](https://github.com/jklasa/heartbeat) for the project hosts the relevant [Python code](https://github.com/jklasa/heartbeat/tree/main/src), [Kubernetes configurations, and](https://github.com/jklasa/heartbeat/tree/main/k8s) [setup scripts](https://github.com/jklasa/heartbeat/tree/main/scripts).

## DockerHub

The images for this project are hosted on DockerHub [here](https://hub.docker.com/repository/docker/jklasa27/heartbeat).

## Code Demonstration

The system is quite large and requires a local Kubernetes cluster, but a sample walkthrough can be found in the navigation on the left. This walkthrough details the processes running in the cluster without running the Kafka cluster, Kubernetes node, or the database.
