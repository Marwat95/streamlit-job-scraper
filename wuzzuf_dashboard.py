import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


# ================= PAGE CONFIG =================
st.set_page_config(page_title="WUZZUF Jobs Dashboard", layout="wide")

st.title("💼 WUZZUF Jobs Scraper Dashboard")
st.write("Scrape and visualize jobs from WUZZUF")

# ================= USER INPUT =================
search_job = st.text_input("Enter job title", placeholder="Data Analyst, Python, SQL")
pages = st.slider("Number of pages", 1, 5, 2)


# ================= SCRAPING FUNCTION =================
def scrape_wuzzuf(search_job, pages):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(options=chrome_options)

    titles = []
    companies = []
    locations = []
    job_types = []
    schedules = []
    links = []

    for page in range(pages):
        url = f"https://wuzzuf.net/search/jobs/?a=hpb&q={search_job}&start={page}"
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("div", class_="css-pkv5jc")

        for job in jobs:
            title = job.find("h2").get_text(strip=True)
            link = job.find("h2").find("a")["href"]

            company = job.find("a", href=True).get_text(strip=True)
            location = job.find("span").get_text(strip=True)

            tags = job.find_all("a", href=True)
            schedule = tags[0].get_text(strip=True) if len(tags) > 0 else "N/A"
            job_type = tags[1].get_text(strip=True) if len(tags) > 1 else "N/A"

            titles.append(title)
            companies.append(company)
            locations.append(location)
            job_types.append(job_type)
            schedules.append(schedule)
            links.append("https://wuzzuf.net" + link)

    driver.quit()

    return titles, companies, locations, job_types, schedules, links


# ================= MAIN BUTTON =================
if st.button("🚀 Start Scraping"):

    with st.spinner("Scraping WUZZUF jobs..."):
        titles, companies, locations, job_types, schedules, links = scrape_wuzzuf(
            search_job, pages
        )

    # ================= DATAFRAME =================
    df = pd.DataFrame({
        "Job Title": titles,
        "Company": companies,
        "Location": locations,
        "Job Type": job_types,
        "Schedule": schedules,
        "Link": links
    })

    # ================= KPIs =================
    st.subheader("📌 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jobs", len(df))
    col2.metric("Companies", df["Company"].nunique())
    col3.metric("Locations", df["Location"].nunique())

    st.markdown("---")

    # ================= TABLE =================
    st.subheader("📄 Scraped Jobs")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.header("📊 Job Market Insights")

    # ================= JOB TYPE CHART =================
    st.subheader("Job Types Distribution")
    job_type_count = df["Job Type"].value_counts()
    st.bar_chart(job_type_count)

    # ================= LOCATION CHART =================
    st.subheader("Top Locations")
    location_count = df["Location"].value_counts().head(10)
    st.bar_chart(location_count)

    # ================= COMPANY CHART =================
    st.subheader("Top Hiring Companies")
    company_count = df["Company"].value_counts().head(10)
    st.bar_chart(company_count)

    # ================= PIE CHART =================
    st.subheader("Job Schedule Share")
    fig, ax = plt.subplots()
    df["Schedule"].value_counts().plot.pie(
        autopct="%1.1f%%",
        startangle=90,
        ax=ax
    )
    ax.set_ylabel("")
    st.pyplot(fig)
