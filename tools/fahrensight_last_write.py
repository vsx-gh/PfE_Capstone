#!/usr/bin/env python3

import boto3
import datetime
import os

def find_last_wtime(event, context):
    """ Finds last write time in DynamoDB table """

    dtime_now = datetime.datetime.utcnow()
    dtime_utc_15_ago = (dtime_now - datetime.timedelta(minutes=15)).strftime('%Y%m%d%H%M%S')

    # Set up SNS queue to handle errors
    sns_handle = boto3.client('sns')
    sns_topic_arn = os.environ['sns_arn']

    # Submit query
    dynamo_table_name = os.environ['last_write_table']
    dynamo_db = boto3.resource('dynamodb')
    last_write_db = dynamo_db.Table(dynamo_table_name)

    # Retrieve data from cursor
    last_write = last_write_db.get_item(Key={'id': 1})['Item']['rectime']

    # See if last written item was more than a quarter-hour ago
    if last_write < dtime_utc_15_ago:
        # Activate e-mail notification
        msg_text = 'WARNING! Last item written to {} > 15 minutes ago. Last write time is {}.'.format(dynamo_table_name, last_write)

        response = sns_handle.publish(
                TopicArn = sns_topic_arn,
                Message = msg_text,
                Subject = 'Fahrensight Stale Write Time'
                )

    return last_write, dtime_utc_15_ago
