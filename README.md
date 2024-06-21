Sackarre
========

Description
-----------
A simple Python script that checks specified pages on marketplaces and alerts
if the price has changed. Should run as AWS lambda. Only lidl.de is supported 
at the moment because I needed to buy something there and waited for a discount
on it.

How it works
------------
Script runs as AWS lambda, stores its data in DynamoDB and puts notifications 
into an SNS topic.

The watched marketplace links and the steps needed to extract them are 
contained in the yaml config that is edited locally and then pushed to the 
DynamoDB storage. 

At the moment the sample probe-lst-example.yaml file contains configuration
that allows watching items on lidl.de.

How to install
--------------
1. Make sure Python is installed on your system
2. `AWS_PROFILE=[your_profile] make aws-deploy`
3. Subscribe to the created 'sackkarre' SNS topic to get the notifications.
4. Edit probes file probe-lst-example.yaml
5. Push the probe list to the cloud storage - 
   `.venv/bin/python main set-probe-list -f probe-lst-example.yaml` 
6. By default, the lambda will not have any triggers. 
   You can set it to run periodically by adding an EventBridge trigger.

