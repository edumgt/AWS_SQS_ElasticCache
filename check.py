import hashlib
import json

# 메시지 본문 (예시)
body = '오늘은 덥지 않습니다. 이건 테스트 메시지입니다.'
expected_md5 = "01220aa2b2166275492f664132f99a16"

# MD5 계산
calculated_md5 = hashlib.md5(body.encode()).hexdigest()

if calculated_md5 == expected_md5:
    print("✅ 메시지 무결성 확인됨!")
else:
    print("❌ 메시지가 손상되었거나 변조되었습니다.")
