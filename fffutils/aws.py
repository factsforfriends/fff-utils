#!/usr/bin/env python

import os
import sys
import boto3

def upload_object(data, key, bucket, content_type = 'image/jpeg', log = None):
    '''
    Uploads a binary data stream to a S3 bucket. Requires ~/.aws/credentials
    '''
    s3 = boto3.resource('s3')

    try: 
        s3.Bucket(bucket).put_object(Key=key, Body=data, ContentType = content_type)
        if log is not None:
            log.debug('Uploading {} to bucket {} on S3'.format(key, bucket))
    except Exception as e:
        if log is not None:
            log.error(e)
        pass