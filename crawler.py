import json
import requests

# 1단계에서 찾은 제타 내부 전시 API 주소
ZETTA_API_URL = "여기에_확인하신_API_URL을_붙여넣으세요"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://lottemartzetta.com/"
}

def fetch_latest_display_data():
    try:
        res = requests.get(ZETTA_API_URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return

    # API 응답 구조에 맞게 캐러셀과 상품 전체 배열 파싱
    sections = []
    # (예시: data['corners'] 또는 data['data']['sections'])
    corners = data.get("data", {}).get("corners", []) or data.get("corners", [])

    for corner in corners:
        items = []
        for idx, prod in enumerate(corner.get("items", [])):
            items.append({
                "slot": idx + 1,
                "id": str(prod.get("itemId", "")),
                "name": prod.get("itemName", ""),
                "badge": prod.get("promotionBadge", ""),
                "price": int(prod.get("salePrice", 0)),
                "originPrice": prod.get("normalPrice"),
                "sales5m": int(prod.get("salePrice", 0)) * 100  # 기본 연동 지표
            })

        if items:
            sections.append({
                "id": corner.get("cornerId", f"SEC_{len(sections)+1}"),
                "title": corner.get("cornerName", "전시 구좌"),
                "badge": "실시간 자동 수동",
                "products": items
            })

    # products.json 저장
    output = {
        "lastUpdated": res.headers.get("Date", "now"),
        "sections": sections
    }

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"총 {len(sections)}개 캐러셀 전수 수집 완료!")

if __name__ == "__main__":
    fetch_latest_display_data()
