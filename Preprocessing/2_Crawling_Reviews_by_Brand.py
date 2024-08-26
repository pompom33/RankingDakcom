# import 파일
import time
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def crawl_page_html(playwright_page, url, max_reviews=1000):
    try:
        playwright_page.goto(url, wait_until="load", timeout=30000)
        print(f"페이지 로드 완료: {url}")
    except Exception as e:
        print(f"페이지 로드 중 오류 발생: {e}")
        return "", []

    time.sleep(1)

    try:
        playwright_page.evaluate("document.querySelector('#orderByRecent').click()")
        print("최신순 정렬 클릭 완료")
    except Exception as e:
        print(f"최신순 정렬 클릭 중 오류 발생: {e}")
        return "", []

    time.sleep(1)

    all_reviews = []
    page_number = 1

    while len(all_reviews) < max_reviews:
        html = playwright_page.content()
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h2", class_='goods-tit').text.strip()
        review_content = soup.find("div", class_='goods-detail-review prodReview')

        if review_content:
            reviews = review_content.find_all("li", class_='review-item')  # 각 리뷰를 개별적으로 다룸

            for review in reviews:
                user = review.find("span", class_='name')
                user_id = user.text.strip() if user else ""  # 개별 리뷰마다 ID 추출

                rating = review.find("em", class_='rating-point')
                rate = rating.find("span", class_="blind").text.strip() if rating else ""

                review_date = review.find("span", class_="date")
                date = review_date.text.strip() if review_date else ""

                eval_box = review.find("div", class_='review-eval-box')
                eval_text = eval_box.text.strip() if eval_box else ""

                review_text = review.find("p", class_='review').text.strip() if review.find("p", class_='review') else ""

                all_reviews.append({
                    "brand": brand,
                    "title": title,
                    "id": user_id,
                    "date": date,
                    "rate": rate,
                    "eval": eval_text,
                    "review": review_text
                })

                if len(all_reviews) >= max_reviews:
                    print(f"리뷰 {max_reviews}개 수집 완료.")
                    return title, all_reviews

        # 다음 페이지로 이동
        next_page_selector = f'#prodReviewList a[data-page="{page_number + 1}"]'
        next_button = playwright_page.locator(next_page_selector)

        try:
            if next_button.is_visible():
                next_button.click()
                page_number += 1
                time.sleep(1)  # 페이지 로드 대기 시간
            else:
                print(f"마지막 페이지 {page_number}까지 크롤링 완료.")
                break  # 더 이상 페이지가 없을 경우 종료
        except Exception as e:
            print("다음 페이지로 이동 중 오류 발생: ", e)
            break

    return title, all_reviews

def write_data(title, data):
    filename = f"./data/{title}.csv"
    with open(filename, "w", encoding="utf-8", newline="") as fw:
        writer = csv.DictWriter(fw, fieldnames=["brand", "title", "id", "date", "rate", "eval", "review"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"{filename} 파일에 저장 완료.")

def main():
    # 링크를 저장한 CSV 파일 읽기
    input_file = './luveat_link_unique.csv'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        playwright_page = browser.new_page()

        with open(input_file, "r", encoding="utf-8") as fr:
            reader = csv.reader(fr)
            links = list(reader)

        # 각 링크에 접속하여 1000개 리뷰 크롤링 및 저장
        for link in links:
            url = link[0]
            title, reviews = crawl_page_html(playwright_page, url, max_reviews=1000)
            write_data(title, reviews)

        browser.close()

if __name__ == "__main__":
    brand = "luveat"
    main()
