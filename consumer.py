import boto3
import hashlib
import json

# SQS 클라이언트 생성
sqs = boto3.client('sqs', region_name='ap-northeast-2')

# 주문 처리 큐 URL — 실제 AWS 계정 ID로 변경 후 사용 (예: 123456789012)
QUEUE_URL = 'https://sqs.ap-northeast-2.amazonaws.com/<account-id>/order-queue'

# 재고 데이터 (간단한 인메모리 예시)
inventory = {
    "PROD-001": 10,
    "PROD-042": 3,
    "PROD-007": 20,
}


def process_order(order: dict):
    """주문 이벤트 처리 — 재고 차감"""
    event = order.get("event")
    if event != "ORDER_PLACED":
        print(f"[재고 서비스] ⚠️ 알 수 없는 이벤트: {event}")
        return

    product_id = order["product_id"]
    quantity = order["quantity"]
    order_id = order["order_id"]

    if product_id not in inventory:
        print(f"[재고 서비스] ❌ 상품 없음: {product_id}")
        return

    if inventory[product_id] < quantity:
        print(f"[재고 서비스] ❌ 재고 부족 — {product_id} (재고: {inventory[product_id]}, 요청: {quantity})")
        return

    inventory[product_id] -= quantity
    print(f"[재고 서비스] ✅ 재고 차감 완료")
    print(f"  OrderId  : {order_id}")
    print(f"  ProductId: {product_id}")
    print(f"  차감 수량 : {quantity}  남은 재고: {inventory[product_id]}")


def receive_and_process(max_messages: int = 10):
    """SQS에서 주문 이벤트를 수신하고 처리"""
    print("[재고 서비스] 📡 주문 이벤트 수신 대기 중...\n")
    processed = 0

    while processed < max_messages:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=5,
            MessageAttributeNames=['All']
        )

        messages = response.get('Messages', [])
        if not messages:
            print("[재고 서비스] 📭 처리할 메시지가 없습니다.")
            break

        for msg in messages:
            body_str = msg['Body']

            # 무결성 검증 (AWS SQS 호환용 MD5 — 암호화 목적이 아닌 전송 오류 감지용)
            expected_md5 = msg['MD5OfBody']
            actual_md5 = hashlib.md5(body_str.encode()).hexdigest()
            if expected_md5 != actual_md5:
                print(f"[재고 서비스] ❌ MD5 불일치 — 메시지 손상 가능성 있음. 건너뜀.")
                continue

            try:
                order = json.loads(body_str)
            except json.JSONDecodeError:
                print(f"[재고 서비스] ❌ JSON 파싱 오류. 건너뜀.")
                continue

            process_order(order)

            # 처리 완료된 메시지 삭제
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )
            print(f"  🗑️ 메시지 삭제 완료\n")
            processed += 1

    print(f"[재고 서비스] 총 {processed}건 처리 완료.")


if __name__ == "__main__":
    receive_and_process()
