import redis

# ElastiCache Redis 엔드포인트와 포트
REDIS_HOST = "edumgt-redis-7c7abo.serverless.apn2.cache.amazonaws.com"  # 예: my-redis.abcd.ng.0001.apn2.cache.amazonaws.com
REDIS_PORT = 6379  # 기본 Redis 포트

# Redis 클라이언트 생성
client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True  # 문자열로 자동 디코딩
)

# 키-값 저장
client.set("message", "안녕하세요, 엘라스티캐시!")

# 키 값 가져오기
value = client.get("message")

print("✅ Redis에서 가져온 값:", value)
