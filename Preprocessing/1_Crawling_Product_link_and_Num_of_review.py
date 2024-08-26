from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import csv

def crawl_link(url):
    # 맨 먼저 '상품 더보기' 버튼을 클릭
    while True:
        try:
            load_more_button = page.locator(".btn-article-md")
            if load_more_button.is_visible():
                load_more_button.click()
                time.sleep(2)  # 페이지 로드 대기
            else:
                print("끝")
                break
        except Exception as e:
            print(e)
            break

    # 더보기가 더이상 없으면 페이지 소스 파싱
    soup = BeautifulSoup(page.content(), 'html.parser')

    # 제품 링크와 리뷰 수 추출
    products = soup.find_all('a', class_='text-elps2')
    with open("./luveat_link.csv", "w", encoding="utf-8", newline="") as fw:
        writer = csv.writer(fw)
        writer.writerow(['Product Link', 'Total Reviews'])  # CSV 헤더 설정

        for product in products:
            # 링크 추출
            product_link = product.get('href')

            # 제품 총 리뷰 수 추출 - 동일한 값의 리뷰 수를 정리하기 위해.
            total_reviews_tag = product.find_next("span", class_="total-num")
            total_reviews = total_reviews_tag.text.strip() if total_reviews_tag else "0"

            writer.writerow([product_link, total_reviews])

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # url에 각 브랜드 메인 페이지 입력.
        url = "https://www.rankingdak.com/display/brand/view?brandCd=1049&searchType=search_sort"
        page.goto(url)
        crawl_link(url)
