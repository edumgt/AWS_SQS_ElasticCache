# AWS SQS & SNS 학습 정리

> 0630 수업 정리본을 보기 좋게 정돈한 문서입니다.

## 목차
- [SQS 개요](#sqs-개요)
- [S3 버킷 공개 정책 예시](#s3-버킷-공개-정책-예시)
- [SQS 큐 생성](#sqs-큐-생성)
- [메시지 송수신](#메시지-송수신)
- [Python(boto3) 테스트](#pythonboto3-테스트)
- [SNS 연동](#sns-연동)
- [민감정보 체크](#민감정보-체크)

---

## SQS 개요
**AWS SQS (Simple Queue Service)**는 메시지를 큐에 넣고 꺼내는 방식으로 시스템 간 **비동기 통신**을 가능하게 하는 서비스입니다.

### 주요 특징
- **비동기 처리**: 생산자(Producer)와 소비자(Consumer)의 처리 속도가 달라도 안정적으로 전달
- **완전관리형**: 서버 구축/유지보수 없이 사용
- **높은 내구성**: 메시지를 다중 복제 저장

### 큐 유형
- **Standard Queue**: 무제한 처리량, 최소 1회 전달 보장, 순서 보장 ❌
- **FIFO Queue**: 정확히 1회 처리, 순서 보장 ✅, 처리량 제한

### 활용 예시
- 주문/결제 처리 비동기화
- 이미지 업로드 후 썸네일 생성
- 마이크로서비스 간 메시지 전달

---

## S3 버킷 공개 정책 예시
> ⚠️ 운영 환경에서는 버킷 공개 정책 적용 시 보안 리스크가 큽니다.

```bash
aws s3api put-bucket-policy \
  --bucket <bucket-name> \
  --policy file://s3-policy.json
```

---

## SQS 큐 생성
```bash
aws sqs create-queue --queue-name my-test-queue
```

### 권한 오류 예시
```text
An error occurred (AccessDenied) when calling the CreateQueue operation: \
User: arn:aws:iam::<account-id>:user/<user-name> is not authorized to perform: \
sqs:CreateQueue on resource: arn:aws:sqs:<region>:<account-id>:my-test-queue
```

### 콘솔 권한 부여 화면
![권한 부여](image.png)

### 생성 결과 예시
```json
{
  "QueueUrl": "https://sqs.<region>.amazonaws.com/<account-id>/my-test-queue"
}
```

### 콘솔 확인
![콘솔 확인](image-1.png)

---

## 메시지 송수신
### 메시지 보내기
```bash
aws sqs send-message \
  --queue-url https://sqs.<region>.amazonaws.com/<account-id>/my-test-queue \
  --message-body '안녕하세요! 이건 테스트 메시지입니다.'
```

```json
{
  "MD5OfMessageBody": "11b4b81379e4a214e981839eae5b94bd",
  "MessageId": "b48bb9d4-4a97-4394-915a-2c1cbfdc4f4c"
}
```

> **MD5OfMessageBody**는 복호화용이 아니라 **무결성 확인용**입니다.

### 메시지 수신
```bash
aws sqs receive-message \
  --queue-url https://sqs.<region>.amazonaws.com/<account-id>/my-test-queue
```

```json
{
  "Messages": [
    {
      "MessageId": "b48bb9d4-4a97-4394-915a-2c1cbfdc4f4c",
      "ReceiptHandle": "...",
      "MD5OfBody": "11b4b81379e4a214e981839eae5b94bd",
      "Body": "안녕하세요! 이건 테스트 메시지입니다."
    }
  ]
}
```

### 무결성 체크 (check.py)
`check.py`에서 `body = '안녕하세요! 이건 테스트 메시지입니다.'`를 변경해가며 확인 가능합니다.

```text
PS> python check.py
❌ 메시지가 손상되었거나 변조되었습니다.
PS> python check.py
✅ 메시지 무결성 확인됨!
```

---

## Python(boto3) 테스트
### boto3 설치
```bash
pip install boto3
```

### 테스트 실행
```bash
python sqs.py
```

### 결과 예시
```text
✅ 메시지 전송 완료
MessageId: b86cc94e-9858-4c87-8629-b9b18e5b37fa
MD5OfMessageBody: 40ca02b8b3f81347d8ceb1b0769de9e3

📩 메시지 수신
Body: {"message": "python으로 테스트 합니다."}
MD5 검증: ✅ 일치
🗑️ 메시지 삭제 완료
```

> 수신을 생략하려면 `sqs.py`의 수신 부분을 주석 처리합니다.

```python
# 2. 메시지 받기
# receive_message()
```

### 콘솔에서 대기 확인
![콘솔 대기 확인](image-2.png)

---

## SNS 연동
**Amazon SNS (Simple Notification Service)**는 이벤트를 여러 구독자에게 푸시(Push)하는 서비스입니다.
SQS, Lambda, Email, HTTP 엔드포인트 등이 구독자가 될 수 있습니다.

### SNS 생성
```bash
aws sns create-topic --name my-sns-topic
```

### 권한 오류 예시
```text
An error occurred (AuthorizationError) when calling the CreateTopic operation: \
User: arn:aws:iam::<account-id>:user/<user-name> is not authorized to perform: \
SNS:CreateTopic on resource: arn:aws:sns:<region>:<account-id>:my-sns-topic
```

### 권한 부여 화면
![SNS 권한 부여](image-3.png)

### ARN 생성 결과 예시
```json
{
  "TopicArn": "arn:aws:sns:<region>:<account-id>:my-sns-topic"
}
```

### SNS용 SQS 큐 생성
```bash
aws sqs create-queue --queue-name my-sns-queue
```

```json
{
  "QueueUrl": "https://sqs.<region>.amazonaws.com/<account-id>/my-sns-queue"
}
```

### 구독자 생성
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:<region>:<account-id>:my-sns-topic \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:<region>:<account-id>:my-sns-queue
```

```json
{
  "SubscriptionArn": "arn:aws:sns:<region>:<account-id>:my-sns-topic:<subscription-id>"
}
```

### 메시지 수신 허용 (SQS 정책 적용)
> JSON 문자열의 따옴표 이스케이프에 주의하세요.

1. `sqs-policy.json` 생성
2. 정책 적용

```bash
aws sqs set-queue-attributes --cli-input-json file://sqs-policy.json
```

3. 적용 확인

```bash
aws sqs get-queue-attributes \
  --queue-url https://sqs.<region>.amazonaws.com/<account-id>/my-sns-queue \
  --attribute-names Policy
```

```json
{
  "Attributes": {
    "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"sns.amazonaws.com\"},\"Action\":\"SQS:SendMessage\",\"Resource\":\"arn:aws:sqs:<region>:<account-id>:my-sns-queue\",\"Condition\":{\"ArnEquals\":{\"aws:SourceArn\":\"arn:aws:sns:<region>:<account-id>:my-sns-topic\"}}}]}"
  }
}
```

### 메시지 발행
```bash
aws sns publish \
  --topic-arn arn:aws:sns:<region>:<account-id>:my-sns-topic \
  --message '안녕하세요! SNS에서 보내는 메시지입니다.'
```

### 콘솔 확인
![SNS 메시지 확인](image-4.png)

### sqs.py 수정 예시
```python
QUEUE_URL = 'https://sqs.<region>.amazonaws.com/<account-id>/my-sns-queue'
```

---

## boto3 소개
boto3는 Python에서 AWS 서비스를 제어할 수 있게 해주는 공식 SDK입니다.

| 기능 구분 | 설명 |
| --- | --- |
| AWS 서비스 제어 | S3, EC2, DynamoDB, IAM, Lambda 등 제어 |
| 리소스 자동화 | 인스턴스 생성, 버킷 생성, 파일 업로드 등 |
| 클라이언트 & 리소스 | `client()`와 `resource()` API 제공 |
| 자격증명 연동 | IAM 사용자/역할, 환경 변수, `~/.aws/credentials` 등 |
| 오케스트레이션 | 예: EC2 생성 → 보안그룹 설정 → S3 설정파일 다운로드 → 시작 스크립트 실행 |

---

## 이메일 예제
`email1.py`, `email2.py`는 SNS 이용 이메일 발송/수신 예시입니다.
> 이메일 수신이 스팸 처리될 수 있으니 주의하세요.

---

## 민감정보 체크
아래 항목은 **실제 계정/리소스 정보가 될 수 있어 문서에 포함될 경우 마스킹**이 권장됩니다.

- **AWS Account ID**
- **IAM 사용자명**
- **ARN / Queue URL / Topic ARN**
- **정책 JSON 내 Resource ARN**

이 문서에서는 위 정보를 `<account-id>`, `<region>`, `<user-name>` 등의 **플레이스홀더로 변경**했습니다.
실제 값은 로컬 환경 변수나 `.env`에 보관하고, 문서/깃에는 올리지 않는 것을 권장합니다.
