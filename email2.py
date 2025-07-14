# (선택적) 이메일 구독자 추가 코드
response = sns.subscribe(
    TopicArn=TOPIC_ARN,
    Protocol='email',
    Endpoint='example@example.com'  # 수신할 이메일 주소
)
print("구독 확인을 이메일로 보냈습니다. 메일을 열어 Confirm 버튼을 클릭하세요.")
