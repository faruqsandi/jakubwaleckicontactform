from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import chromedriver_autoinstaller


chromedriver_autoinstaller.install()
options = Options()
# options.add_argument('--headless')  # Remove this line if you want to see the browser
service = Service()
driver = webdriver.Chrome(service=service, options=options)


url = "https://50safe.pl/"
# Step 1: Open Google
driver.get(url)

source = driver.page_source

soup = BeautifulSoup(source, "html.parser")

links = soup.find_all("a")


link_list = []
# Extract text and href
for link in links:
    text = link.get_text(strip=True)
    href = link.get("href")
    if href and text:
        if href == "#":
            continue
        href = urljoin(url, href)  # Make sure href is absolute
        link_list.append((text, href))

# Step 2: Search for something
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("site:openai.com ChatGPT")
search_box.send_keys(Keys.RETURN)

# Wait for results to load
time.sleep(2)  # Replace with WebDriverWait if needed

# Step 3: Click first result
first_result = driver.find_element(By.CSS_SELECTOR, "h3")
first_result.click()

# Step 4: Wait and print title of the result page
time.sleep(2)  # Replace with WebDriverWait if needed
print("Page title:", driver.title)

driver.quit()
