#!/usr/bin/env python3
# scripts/seed_webhook.py
"""
Script bắn Mock Webhook & Test Events vào các Microservices Local phục vụ kiểm thử E2E.
Hỗ trợ:
  - Bắn sự kiện Capture vào PostHog Backend (port 8000 / 8080)
  - Bắn sự kiện Tạo đơn hàng vào Order Service (port 5001)
  - Bắn sự kiện Webhook vào Worker Service (port 3000)
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
import time

def send_request(url: str, payload: dict, headers: dict = None) -> tuple[int, str]:
    if headers is None:
        headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)

def seed_posthog_event(host: str = "http://127.0.0.1:8000", distinct_id: str = "test_user_01", event_name: str = "e2e_test_event"):
    url = f"{host}/capture/"
    payload = {
        "api_key": "local_dev_key",
        "event": event_name,
        "distinct_id": distinct_id,
        "properties": {
            "$current_url": "http://localhost:8080/insights",
            "test_source": "seed_webhook_script",
            "timestamp": time.time(),
        }
    }
    print(f"🚀 Đang gửi Event tới PostHog Capture: {url}")
    status, body = send_request(url, payload)
    print(f"   Kết quả: HTTP {status} | Phản hồi: {body[:150]}")
    return status in [200, 201]

def seed_order_service(host: str = "http://127.0.0.1:5001", order_id: str = "ORD-TEST-001", amount: float = 99.9):
    url = f"{host}/api/orders"
    payload = {
        "order_id": order_id,
        "customer_id": "cust_123",
        "amount": amount,
        "currency": "USD",
        "status": "CREATED"
    }
    print(f"📦 Đang gửi Đơn hàng tới Order Service: {url}")
    status, body = send_request(url, payload)
    print(f"   Kết quả: HTTP {status} | Phản hồi: {body[:150]}")
    return status in [200, 201]

def main():
    parser = argparse.ArgumentParser(description="Bắn Mock Data / Webhook cho kiểm thử E2E Local")
    parser.add_argument("--url", type=str, default="", help="URL webhook đích (tùy chỉnh cho mọi dự án)")
    parser.add_argument("--payload", type=str, default="", help="JSON string dữ liệu gửi kèm")
    parser.add_argument("--target", choices=["custom", "event", "order", "all"], default="all", help="Dịch vụ đích cần nhận mock event")
    parser.add_argument("--event", type=str, default="e2e_sample_event", help="Tên event cần bắn")
    parser.add_argument("--user", type=str, default="user_local_e2e", help="Distinct ID của user")
    args = parser.parse_args()

    print("=" * 65)
    print("🌱 [SEED WEBHOOK] KÍCH HOẠT SEED DỮ LIỆU THỬ NGHIỆM CHO E2E")
    print("=" * 65)

    if args.url:
        payload_data = json.loads(args.payload) if args.payload else {"event": args.event, "timestamp": time.time()}
        print(f"🚀 Đang gửi Custom Webhook tới: {args.url}")
        status, body = send_request(args.url, payload_data)
        print(f"   Kết quả: HTTP {status} | Phản hồi: {body[:150]}")
        sys.exit(0 if status in [200, 201] else 1)

    if args.target in ["event", "all"]:
        # Mặc định thử bắn tới event ingestion trên port 8000 hoặc 5001
        seed_posthog_event(event_name=args.event, distinct_id=args.user)

    if args.target in ["order", "all"]:
        seed_order_service()

    print("=" * 65)
    print("✅ Hoàn tất bắn mock data!")

if __name__ == "__main__":
    main()
