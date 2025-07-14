import boto3

# === 설정 ===
REGION = 'ap-northeast-2'  # 서울 리전
TOPIC_ARN = 'arn:aws:sns:ap-northeast-2:086015456585:my-sns-topic'  # 실제 ARN으로 변경

# === 클라이언트 생성 ===
sns = boto3.client('sns', region_name=REGION)

# === 메시지 발송 ===
response = sns.publish(
    TopicArn=TOPIC_ARN,
    Subject='[테스트] SNS 이메일 발송',
    Message='이메일로 보내는 AWS SNS 테스트 메시지입니다.'
)

print("메시지 ID:", response['MessageId'])
