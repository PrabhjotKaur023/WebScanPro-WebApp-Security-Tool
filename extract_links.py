import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE, "login.php")
START_URL = urljoin(BASE, "index.php")

session = requests.Session()

visited = set()
urls = []


# -------- LOGIN --------
login_page = session.get(LOGIN_URL)
soup = BeautifulSoup(login_page.text, "html.parser")

token = soup.find("input", {"name": "user_token"})
token_value = token["value"] if token else ""

login_data = {
    "username": "admin",
    "password": "password",
    "Login": "Login",
    "user_token": token_value
}

login_response = session.post(LOGIN_URL, data=login_data)

if "logout.php" not in login_response.text.lower():
    print("Login failed")
    exit()

print("Login successful")

# 🔥 IMPORTANT FIX
session.cookies.set("security", "low")


# -------- CRAWLER FUNCTION --------
def crawl(url):

    if url in visited:
        return

    visited.add(url)

    try:
        response = session.get(url)

        # skip if redirected to login
        if "login.php" in response.url:
            return

        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):

            full_url = urljoin(BASE, link["href"])

            if full_url.startswith(BASE) and full_url not in visited:
                urls.append(full_url)
                crawl(full_url)

    except Exception as e:
        print("Error:", e)


# -------- START --------
crawl(START_URL)

# remove duplicates
urls = list(set(urls))


# -------- SAVE --------
with open("urls.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=4)

print("All URLs saved to urls.json")