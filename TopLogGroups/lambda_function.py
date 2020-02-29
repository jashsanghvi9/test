import json
import boto3
import os

# ================ Fetching SNS Topic ARN  =====================
SNS_Topic_ARN = os.environ["outbound_topic_arn"]
# ==========================================================

def lambda_handler(event, context):
    
    #message = json.dumps(event)
    #print("=====================================")
    #print(message)
    #print("=====================================")
    
    #=============== Extracting Values 1 =================
    instance_id = event['detail']['instance-id']
    status = event['detail']['state']
    #=====================================================
    
    client = boto3.client('ec2')
    response_ec2 = client.describe_instances(
        InstanceIds=[instance_id]
    )
    
    #=============== Extracting Values of EC2 instance ======================
    allTags = response_ec2['Reservations'][0]['Instances'][0]['Tags']
    publicDNS = response_ec2['Reservations'][0]['Instances'][0]['PublicDnsName']
    privateDNS = response_ec2['Reservations'][0]['Instances'][0]['PrivateDnsName']
    #=====================================================
    
    print("=====================Name Tag Logic =====================") 
    nameTag = 'null'
    for item in allTags:
        #print(item)
        if item['Key'] == 'Name':
            x= len(item['Value'])
            if x == 0:
                print('Blank Name Tag for Instance-Id - '+instance_id)
            else:
                nameTag = item['Value']
    #=====================================
    if nameTag == 'null':
        AlarmName = instance_id
        print('No Name-Tag assigned for Instance-Id - '+instance_id+'. Using Instance-Id to create the Alarm')
    else:
        AlarmName = nameTag
        print('Using Name Tag - '+AlarmName+' for Instance-Id - '+instance_id)
    #=====================================
        
    print("================ Final Check =====================")
    print('1. state = '+status)
    print('2. Instance-id = '+instance_id)
    print('3. Name Tag = '+nameTag)
    print('4. Public DNS = '+publicDNS)
    print('5. Private DNS = '+privateDNS)
    print("==================================================")
    
    ## ======================== Alarm Creation Logic ===========================
    client = boto3.client('cloudwatch')
    
    if status == 'running':
        print("=====================================")
        print('Creating a New Alarm - "EC2-StatusCheck-' +AlarmName+ '".')
    
        response = client.put_metric_alarm(
            AlarmName='EC2-StatusCheck-' +AlarmName,
            AlarmDescription='EC2-StatusCheck',
            ActionsEnabled=True,
            AlarmActions=[SNS_Topic_ARN],
            MetricName='StatusCheckFailed',
            Namespace='AWS/EC2',
            Statistic='Maximum',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            Period=60,
            EvaluationPeriods=2,
            DatapointsToAlarm=2,
            Threshold=1,
            ComparisonOperator='GreaterThanOrEqualToThreshold'
        )
        print(response)
        print("=====================================")
        
    elif status == 'terminated':
        print("=====================================")
        print('Deleting Alarm - "EC2-StatusCheck-' +AlarmName+'". Deleting Alarm - "EC2-StatusCheck-' +instance_id+'".')
        response = client.delete_alarms(
            AlarmNames=['EC2-StatusCheck-' +AlarmName, 'EC2-StatusCheck-' +instance_id]
        )
        print(response)
        print("=====================================")
    
    else:
        print("=====================================")
        print('No action for ' + status + ' state')
        print("=====================================")
## ======================== FIn ===========================