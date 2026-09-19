import json
import re
import requests
from bs4 import BeautifulSoup

# 스마트센터 메인 URL
TARGET_URL = "https://lottemartzetta.com/?ch_no=100050&ch_dtl_no=1000287"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawl_zetta_main():
    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
        html = res.text
    except Exception as e:
        print(f"Fetch error: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")
    carousels = []

    # 1. HTML 내 __NEXT_DATA__ 또는 인라인 JSON 상태값 우선 탐색 (SPA 구조 대응)
    script_data = soup.find("script", id="__NEXT_DATA__")
    if script_data:
        try:
            data = json.loads(script_data.string)
            # JSON 내 코너/캐러셀 데이터가 존재할 경우 파싱 로직 수행
            # (구조에 따라 직접 키 추출 가능)
        except Exception:
            pass

    # 2. DOM 파싱: 각 섹션 컨테이너 및 가로 스와이프 캐러셀 블록 탐색
    sections = soup.select("section, div[class*='section'], div[class*='corner']")
    
    for sec_idx, sec in enumerate(sections):
        title_tag = sec.select_one("h2, h3, strong, [class*='title']")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        if len(title) < 2:
            continue

        # 캐러셀 내의 모든 상품 링크/카드 탐색 (숨겨진 슬롯 포함)
        cards = sec.select("a[href*='/product/'], div[class*='product'], div[class*='item']")
        items = []

        for idx, card in enumerate(cards):
            name_tag = card.select_one("[class*='name'], [class*='title'], p")
            price_tag = card.select_one("[class*='price'], strong, span[class*='sale']")

            link = card.get("href", "") or (card.select_one("a").get("href", "") if card.select_one("a") else "")
            id_match = re.search(r"\d{6,}", link)
            prod_id = id_match.group(0) if id_match else f"P_{idx+1}"

            name = name_tag.get_text(strip=True) if name_tag else ""
            raw_price = price_tag.get_text(strip=True) if price_tag else "0"
            price_digits = re.sub(r"[^\d]", "", raw_price)
            price = int(price_digits) if price_digits else 0

            if name and not any(it["name"] == name for it in items):
                items.append({
                    "slot": len(items) + 1,
                    "id": prod_id,
                    "name": name,
                    "price": price,
                    # 초기 가상 5분 매출/점유율 산정용 기본값
                    "sales5m": price * max(1, (20 - len(items))) * 3
                })

        if len(items) >= 2:
            carousels.append({
                "id": f"SEC_{sec_idx+1}",
                "title": title,
                "badge": "실시간 수집",
                "totalItems": len(items),
                "products": items
            })

    # 추출 결과 저장
    output = {
        "lastUpdated": res.headers.get("Date", "recent"),
        "sections": carousels
    }

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Crawling complete: {len(carousels)} carousels saved to products.json")

if __name__ == "__main__":
    crawl_zetta_main()
