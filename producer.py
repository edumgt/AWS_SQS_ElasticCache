import boto3
import json
import uuid
from datetime import datetime

# SQS 클라이언트 생성
sqs = boto3.client('sqs', region_name='ap-northeast-2')

# 주문 처리 큐 URL — 실제 AWS 계정 ID로 변경 후 사용 (예: 123456789012)
QUEUE_URL = 'https://sqs.ap-northeast-2.amazonaws.com/<account-id>/order-queue'


def create_order(product_id: str, quantity: int, customer_id: str) -> dict:
    """주문 이벤트 생성"""
    return {
        "event": "ORDER_PLACED",
        "order_id": str(uuid.uuid4()),
        "product_id": product_id,
        "quantity": quantity,
        "customer_id": customer_id,
        "timestamp": datetime.utcnow().isoformat()
    }


def send_order_event(order: dict):
    """주문 이벤트를 SQS로 전송 (주문 서비스 → 재고 서비스)"""
    body_str = json.dumps(order, ensure_ascii=False)
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=body_str,
        MessageAttributes={
            'event_type': {
                'StringValue': order['event'],
                'DataType': 'String'
            }
        }
    )
    print(f"[주문 서비스] ✅ 주문 이벤트 전송 완료")
    print(f"  OrderId  : {order['order_id']}")
    print(f"  ProductId: {order['product_id']}")
    print(f"  Quantity : {order['quantity']}")
    print(f"  MessageId: {response['MessageId']}")
    return response


if __name__ == "__main__":
    # 주문 이벤트 3건 전송
    orders = [
        ("PROD-001", 2, "CUST-101"),
        ("PROD-042", 1, "CUST-202"),
        ("PROD-007", 5, "CUST-303"),
    ]
    for product_id, quantity, customer_id in orders:
        order = create_order(product_id, quantity, customer_id)
        send_order_event(order)
        print()
