import boto3
import json
import datetime
from json import dumps
import operator
import re
import os

## + ========================================= + Customer Defination Part + ========================================= +
# Define number of days
number_of_days = os.environ['number_of_days']
# Define top 4 or top 10,
top = os.environ['top']
# Define Subject name for the Email Notification
subject_name = "Top " + str(top) + " Log Group for IncomingBytes in last " + str(number_of_days) + " days."
#Define SNS Topic ARN
sns_topic_arn = os.environ['sns_topic_arn']
## + ========================================= + Customer Defination Part End + ========================================= +
 
 
#Creating empty dictionary
mydict= {}


def lambda_handler(event, context):
    client = boto3.client('cloudwatch')
    
    # Make List Metrics API call.
    response = client.list_metrics(
        Namespace='AWS/Logs',
        MetricName='IncomingBytes'
    )
    #print response
  
    #Converting days to seconds
    hours = (int(number_of_days) * 24)
    seconds = (hours * 3600)

    # Getting Log Group name from Response JSON.
    for item in response['Metrics']:
        for get_dimensions in item['Dimensions']:
            loggroup_name = get_dimensions['Value']
            #print loggroup_name
  
            # Make Get Metric Statistics API call for each Log Group
            response = client.get_metric_statistics(
                Namespace='AWS/Logs',
                MetricName='IncomingBytes',
                Dimensions=[
                    {
                    'Name': 'LogGroupName',
                    'Value': get_dimensions['Value']
                    },
                ],
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=seconds),
                EndTime=datetime.datetime.utcnow(),
                Period=seconds,
                Statistics=[
                    'Sum',
                ]
            )
            #Getting Data points for Log Group name from response.
            for item in response['Datapoints']:
                    val = int(item['Sum'])
                    #print val
                    mydict[val] = loggroup_name
    print '+ =========================== Sorting Top Five ================================= +'
    sorted_x = sorted(mydict.items(), key=operator.itemgetter(0),reverse=True)
    top_five = sorted_x[:int(top)]
    strin = ""
    for x,y in top_five:
        strin = strin +  y + " : " + str (x) + " Bytes" + "\n"
    print 'UTC --> ' + str(datetime.datetime.utcnow())
    print strin
  
    print '+ =========================== Starting SNS Process ================================= +'
    client = boto3.client('sns')
    response = client.publish(
        TargetArn=sns_topic_arn,
        Message=strin,
        MessageStructure='string',
        Subject = subject_name
    )
    print response
    print '+ =========================== + Fin + ================================= +'