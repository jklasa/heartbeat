---
layout: default
title: Diagnosis
nav_order: 5
description: ""
permalink: /6ds/diagnosis
parent: 6Ds
---

# Diagnosis

## Failure Modes

Failure modes in this system largely concerned the internal manipulation of data and the sourcing of that data. There is a lot of data to track and analyze, which produces difficulties on its own. The sourcing of that data is entirely user dependent, and can largely shift the results of the Heartbeat analysis. Careful consideration needs to be used when setting up Heartbeat and analyzing its results. Notably, external or expert assistance could be valuable here, as described in the section on [domain expertise](/heartbeat/6ds/domain-expertise).

## Bias and Ethics

### Scoping and Mapping

For analysis of the bias and ethics involved, I will specifically consider the application of Heartbeat to the task of understanding social media malign influence campaigns on the subject of the Russia-Ukraine war.

In scoping, results from such an analysis could alter the way users of social media platforms perceive content and interact with the platforms themselves, so it is important that the results are accurate, treated carefully, and free of personal bias. Fortunately, this is mostly a proof of concept, so I would not expect initial results to have great impact.

Open access to aggregated data in this form is an interesting idea and one I think should be considered for more informed use of social networks. While constructing this system, I discovered the limitations of my access to aggregate Twitter data (even with Elevated access), and I couldn't help but wonder what could be done with orders of magnitude more data. Operators of these social networks have access to such data and are undoubtedly running analysis on it. This raises the questions, what analyses are being run, and what are the results? What can they see that we cannot?

For better or worse, the scope of this system is much smaller than this, so such considerations are beyond its current capabilities.
 
If this were a dedicated project, interviews with social media users and platform owners or managers would be useful here to help steer the project towards more complete accountability. Getting usable results from the system is a good start, but pushing those results out to interested parties for making better-informed users is a good stretch goal. As a result, it would be ideal if users themselves and involved parties could help shape its progress.
 
### Artifact Collection

Data stored in long-term storage is minimal in this system: only sentiment results and times are stored. Tweet IDs are the only Twitter-based attributes stored from each Tweet. This is done to preserve disk space on my local system and to reduce the amount of personal user data stored on a private system.

Additionally, Twitter requires the removal of data that has been requested to be removed by users. This removal helps keep data compliant with the desires of the users and owners of that data: the data I am using in the model prediction is not completely free for use and must be maintained properly. By only storing Tweet IDs, I can provide reference for analysis results while still remaining compliant with user privacy and Twitter's compliance requirements.
 
### Testing, Reflection, and Post-Audit

Verification of results by external sources and tracking drift would be useful to support findings and actions taken based on those findings. Verification that the results have not been exploited in an adversarial manner would be useful as well.

This verification can be difficult, however, as the whole purpose of the system is to track changes. By keeping the model current to current Tweet data (such as the data used in the training of the Heartbeat model), the hope is changes in sentiment can be traced back to changes in opinion and not just changes in language and model drift. Additionally, using a model trained to better handle language model degradation and language drift should help with this.
 
In the reflection and later stages of the system's use, it will be important to evaluate the impact and success of the system. It would be beneficial as wel to continue to update as necessary for new changes to influences campaigns and social media platforms are made. It is difficult to assess the impact of such a system up front, so this type of continuous monitoring would be quite constructive.
