import boto3
import json


client = boto3.client('cloudwatch')
response = client.get_metric_widget_image(
    MetricWidget='{\"metrics\":[[\"AWS\/EC2\",\"CPUUtilization\",\"InstanceId\",\"i-0833b32280ed5370e\",{\"accountId\":\"564077728039\"}]],\"view\":\"timeSeries\",\"stacked\":false,\"region\":\"us-east-1\",\"stat\":\"Average\",\"period\":10,\"title\":\"Plex-CPUUtilization\",\"start\":\"-PT3H\",\"end\":\"P0D\"}'
)

image = response['MetricWidgetImage']
#print image
