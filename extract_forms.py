import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE = "http://localhost:8080/"
LOGIN_URL = BASE + "login.php"

session = requests.Session()


# ---------- LOGIN ----------
def login():
    res = session.get(LOGIN_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    token_value = token["value"] if token else ""

    data = {
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": token_value
    }

    login = session.post(LOGIN_URL, data=data)

    if "logout.php" in login.text:
        print("[+] Login successful")
    else:
        print("[-] Login failed")
        exit()

    session.cookies.set("security", "low")


# -------- LOAD URLS --------
with open("urls.json", "r") as f:
    urls = json.load(f)

forms_data = []


# -------- EXTRACT FORMS --------
def extract_forms(url):
    try:
        response = session.get(url)

        # 🔥 SKIP if redirected to login
        if "login.php" in response.url:
            return

        soup = BeautifulSoup(response.text, "html.parser")
        forms = soup.find_all("form")

        for form in forms:
            action = form.get("action")

            if action:
                action = urljoin(BASE, action)
            else:
                action = url

            method = form.get("method", "get").lower()

            inputs = []

            for inp in form.find_all("input"):
                inputs.append({
                    "name": inp.get("name"),
                    "type": inp.get("type", "text")
                })

            form_details = {
                "page": url,
                "action": action,
                "method": method,
                "inputs": inputs
            }

            forms_data.append(form_details)

    except Exception as e:
        print("Error scanning:", url, e)


# ---------- MAIN ----------
login()

for url in urls:
    print("Scanning:", url)
    extract_forms(url)


# -------- REMOVE DUPLICATES --------
unique_forms = []
seen = set()

for form in forms_data:
    key = json.dumps(form, sort_keys=True)

    if key not in seen:
        seen.add(key)
        unique_forms.append(form)


# -------- SAVE --------
with open("forms.json", "w", encoding="utf-8") as f:
    json.dump(unique_forms, f, indent=4)

print("\nForms saved to forms.json")