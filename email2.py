import boto3

sns = boto3.client('sns', region_name='ap-northeast-2')

TOPIC_ARN = 'arn:aws:sns:ap-northeast-2:086015456585:my-sns-topic'   # 실제 ARN으로 수정
email_list = [
    'kimdy@gmail.com',
    'info@edumgt.co.kr',
    'sangsanq@naver.com'
]

for email in email_list:
    response = sns.subscribe(
        TopicArn=TOPIC_ARN,
        Protocol='email',
        Endpoint=email
    )
    print(f"{email} → 구독 요청 전송됨. 수신자 이메일에서 확인 필요.")
