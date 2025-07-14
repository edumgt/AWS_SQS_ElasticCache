import boto3

s3 = boto3.client('s3')
s3.upload_file('image-1.png', 'test2-edumgt', 'image-1.png')
