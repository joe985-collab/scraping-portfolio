import re
from playwright.sync_api import Page, expect

from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import time

def job_json(job_title,job_exp,job_loc,job_desc,job_links,job_posted):
    
    data = {}
    total_data = []



    data["title"] = job_title
    data["experience"] = job_exp
    data["job_link"] = job_links
    data["location_and_type"] = job_loc
    data["trimmed_description"] = job_desc
    data["posted_on"] = job_posted
    data["scraped_on"] = now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_data.append(data)

    return total_data



def scrape_pages(limit=5):

    page_count = 0
    retry_count = 1
    total = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.naukri.com/")
        # texts = page.locator("h3").inner_text()
        page.get_by_placeholder("Enter skills / designations / companies").fill("python")
        # print(texts)

        page.locator(".qsbSubmit").click()

        while page_count<limit:

                if retry_count > 3: 
                    print("Mission Failed...")
                    break
                try:
                        print("Page Number: ",page_count)
                        page.wait_for_selector(".srp-jobtuple-wrapper")
                        cards = page.locator(".srp-jobtuple-wrapper")
                        print("kkkk")
                        page.wait_for_timeout(5000)

                        for i in range(cards.count()):
                            card = cards.nth(i)

                            job_title = card.locator(".title").inner_text()
                            job_links = card.locator("a.title").evaluate("a => a.href")
                            job_exp = card.evaluate("""
                                el => el.querySelector('.expwdth')?.innerText.trim() || null
                            """)
                            job_loc = card.evaluate("""
                                el => el.querySelector('.locWdth')?.innerText.trim() || null
                            """)
                            job_desc = card.locator(".job-desc").inner_text()
                            job_posted = card.locator(".job-post-day").inner_text()
                            all_page_data = job_json(job_title,job_exp,job_loc,job_desc,job_links,job_posted)
                            print(all_page_data)
                            total += all_page_data
                            # print(len(job_links))
                            # print(len(job_exp))
                            # print(len(job_desc))
                            # print(len(job_title))
                            # print(len(job_loc))
                            # print(len(job_posted))


                  
                        page_count += 1
                        # page.get_by_text("Next").click()
                        page.get_by_role("link", name="Next").click()

                        print("going to next page...")
                        print("------here--------")
                
                except Exception as e:
                        print(f"Something went wrong: {e}, retrtying : {retry_count}")
                        time.sleep(retry_count*2)
                        retry_count += 1
                    

        print(len(total))
        with open("page_1_datas.json", "w", encoding="utf-8") as f:
                json.dump(total, f)
        # print(len(job_title))
        # print(len(job_exp))
        # print(len(job_loc))
        # print(len(job_desc))
        page.wait_for_timeout(5000)  # 3 seconds
        browser.close()

if __name__ == "__main__":
    print("Here")
    scrape_pages()