from __future__ import division
import subprocess
import time
import boto3
import socket
import argparse

parser = argparse.ArgumentParser(description='Parameters for script')
parser.add_argument('--filepath', type=str, default=None)
parser.add_argument('--dimension', type=str, default=None)
parser.add_argument('--region', type=str, default=None)
args = parser.parse_args()
region = args.region
session = boto3.Session(region_name=region)
ec2_client = session.client('ec2')

hostname = socket.gethostname()
logFile = args.filepath
dimension = args.dimension + "-" + hostname


def monitorLog(logFile):
    print "Monitor real time log file: {0}".format(logFile)
    count = 0
    stoptime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 60*5))
    popen = subprocess.Popen(["tail", "-F", logFile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = popen.stdout.readline()
        if line:
            if '"Event":"End"' in line:
                count = count + 1
        thistime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if thistime >= stoptime:
            tps = round(count/300, 4)
            # print "TPS = {0}".format(tps)
            put_data(thistime, tps)
            count = 0
            stoptime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 60*5))


def put_data(timestamp, data):
    cloudwatch_client = boto3.client('cloudwatch', region_name=region)
    cloudwatch_client.put_metric_data(
    Namespace='CUSTOM_NAMESPACE',
    MetricData=[
        {
            'MetricName': 'TPS',
            'Dimensions': [
                {
                    'Name': 'EC2 instance',
                    'Value': dimension
                }
            ],
            'Timestamp': timestamp,
            'Value': data
        }
    ]
)


if __name__ == '__main__':
    monitorLog(logFile)
