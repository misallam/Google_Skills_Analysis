import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.google.com/about/careers/applications/jobs/results/?category=DATA_CENTER_OPERATIONS&category=DEVELOPER_RELATIONS&category=HARDWARE_ENGINEERING&category=INFORMATION_TECHNOLOGY&category=MANUFACTURING_SUPPLY_CHAIN&category=NETWORK_ENGINEERING&category=PRODUCT_MANAGEMENT&category=PROGRAM_MANAGEMENT&category=SOFTWARE_ENGINEERING&category=TECHNICAL_INFRASTRUCTURE_ENGINEERING&category=TECHNICAL_SOLUTIONS&category=TECHNICAL_WRITING&q=%22software%20engineer%22&_gl=1*18o8vns*_ga*MTM1NTM3MjQ5LjE3MzM5MTA3Mjc.*_ga_41NEC9ZD62*MTczMzkxMDcyNi4xLjEuMTczMzkxMDc1My4wLjAuMA&page="

def scrape_job_details(job_url):
    response = requests.get(job_url)
    soup = BeautifulSoup(response.content, "html.parser")

    job_data = {}
    try:
        job_title = soup.find("h2", class_="p1N2lc").text.strip()
        job_data["title"] = job_title

        job_level = soup.find("span", class_="wVSTAb").text.strip()
        job_data["level"] = job_level

        qualifications_div = soup.find("div", class_="KwJkGe")

        min_quals = qualifications_div.find("h3", string="Minimum qualifications:").find_next("ul")
        job_data["minimum_qualifications"] = [li.text.strip() for li in min_quals.find_all("li")]

        pref_quals = qualifications_div.find("h3", string="Preferred qualifications:").find_next("ul")
        job_data["preferred_qualifications"] = [li.text.strip() for li in pref_quals.find_all("li")]

    except AttributeError:
        print(f"Failed to extract some details for URL: {job_url}")

    return job_data

all_jobs = []

current_page = 1
while current_page <= 688:
    print(f"Scraping page {current_page}...")
    response = requests.get(base_url + str(current_page))
    soup = BeautifulSoup(response.content, "html.parser")

    job_listings = soup.find("ul", class_="spHGqe")
    if not job_listings:
        print("No job listings found on this page.")
        break

    for job in job_listings.find_all("a", class_="WpHeLc VfPpkd-mRLv6 VfPpkd-RLmnJb"):
        job_url = job["href"]
        if not job_url.startswith("http"):
            job_url = "https://www.google.com/about/careers/applications/" + job_url if job_url.startswith("/") else "https://www.google.com/about/careers/applications/" + job_url
        job_data = scrape_job_details(job_url)
        all_jobs.append(job_data)

    current_page += 1

df = pd.DataFrame(all_jobs)
df.to_excel("google_se_jobs.xlsx", index=False)
