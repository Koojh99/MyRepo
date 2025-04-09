from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup

import pandas as pd
import time

import pymysql


# 1. ChromeDriver 경로 지정
chromedriver_path = "C:/Workspace/Python/SKN13_boooms/chromedriver-win64/chromedriver.exe"  # 예: "C:/chromedriver.exe" 또는 "/usr/local/bin/chromedriver"

options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 헤드리스 모드 (브라우저 UI 없이 실행)

service = Service(chromedriver_path)

driver = webdriver.Chrome(service=service, options=options)

# 2. driver 통한 페이지 이동
driver.get("https://taas.koroad.or.kr/sta/acs/exs/typical.do?menuId=WEB_KMP_OVT_UAS_ASA")

wait = WebDriverWait(driver, 10)

# 3. 교통사고(DB) 접근
accident_db_selector = '#ddMenuTree0 > div:nth-child(3) > a.node'
accident_db_link = driver.find_element(By.CSS_SELECTOR, accident_db_selector)
accident_db_link.click()
time.sleep(2)

# 3. 교통사고(DB) 중분류 접근
by_accident_selector = '#ddMenuTree17 > div:nth-child(11) > a.node'
by_accident_link = driver.find_element(By.CSS_SELECTOR, by_accident_selector)
by_accident_link.click()
time.sleep(2)

# 4. 유형별 교통사고 접근
by_driver_accident_type_selector = '#sdMenuTree79'
by_driver_accident_type_link = driver.find_element(By.CSS_SELECTOR, by_driver_accident_type_selector)
by_driver_accident_type_link.click()
time.sleep(2)

# 5. 연도(드랍다운박스) 선택
# driver.find_element(By.CSS_SELECTOR, '#startYear').click()
# time.sleep(2)
# dropdown = Select(driver.find_element(By.CSS_SELECTOR, '#stratYear'))
# dropdown.select_by_visible_text('2023년').click()
# time.sleep(2)

# driver.find_element(By.CSS_SELECTOR, '#endYear').click()
# time.sleep(2)
# dropdown = Select(driver.find_element(By.CSS_SELECTOR, '#endYear'))
# dropdown.select_by_visible_text('2023년').click()
# time.sleep(2)

# 6. 조회버튼 클릭
driver.find_element(By.CSS_SELECTOR, '#searchDiv > ul.top01-03 > li:nth-child(2) > input').click()

time.sleep(5)

# iframe 전환
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print("Number of iframes:", len(iframes))
print(iframes)
driver.switch_to.frame('eosFrame')


# 전환된 iframe 내 html 소스 BeautifulSoup으로 파싱싱
soup = BeautifulSoup(driver.page_source, 'html.parser')

# print(soup.find('div', class_ = "ovReportArea ovGridPanel"))

# table 접근 후 데이터 파싱
label_rows = soup.select("#OctagonGrid > tbody > tr")
age_measure_labels = []

current_age_group = None
for row in label_rows:
    cells = row.find_all("td")
    if len(cells) == 2:
        age_td, measure_td = cells
        if age_td.get("rowspan"):
            current_age_group = age_td.get_text(strip=True)
        measure = measure_td.get_text(strip=True)
    elif len(cells) == 1:
        measure = cells[0].get_text(strip=True)
    else:
        continue

    age_measure_labels.append((current_age_group, measure))

# 사고 건수 데이터 추출
data_rows = soup.select("#dataSession > tbody > tr")
accident_type_headers = ["합계", "차대사람", "차대차", "차량단독", "철길건널목"]

all_data = []
for idx, row in enumerate(data_rows):
    values = [td.get_text(strip=True).replace(',', '') for td in row.find_all("td")]
    age, measure = age_measure_labels[idx]
    for i, value in enumerate(values):
        all_data.append({
            "연령대": age,
            "지표": measure,
            "사고유형": accident_type_headers[i],
            "건수": value
        })

print(all_data)

df = pd.DataFrame(all_data)

# CSV 파일로 저장
csv_path = "accidents_by_age_and_type.csv"
df.to_csv(csv_path, index=False)

print(f"CSV 파일이 저장되었습니다: {csv_path}")

connection =  pymysql.connect(host="192.168.0.25",
                                     port=3306,
                                     user="test-connection",
                                     password="12345678",
                                     db="01_proj")

# 출력 예시
# df = pd.DataFrame(all_data)
# print(df)
cursor = connection.cursor()


accident_type_df = pd.DataFrame({
    "id": ["AT1", "AT2", "AT3", "AT4"],
    "type_name": ["차대사람", "차대차", "차량단독", "철길건널목"]
})

age_group_df = pd.DataFrame({
    "id": ["AG1", "AG2", "AG3", "AG4", "AG5", "AG6", "AG7"],
    "age_range": ["20세이하", "21~30세", "31~40세", "41~50세", "51~60세", "61~64세", "65세이상"]
})

time_slot_df = pd.DataFrame({
    "id": ["TS1"],
    "time_range": ["전체"]
})

# INSERT 함수


# 실제 삽입











driver.close()