import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE = "http://localhost:8080/"

session = requests.Session()

# -------- LOAD URLS --------
with open("urls.json", "r") as f:
    urls = json.load(f)

forms_data = []

# -------- FUNCTION TO EXTRACT FORMS --------
def extract_forms(url):
    try:
        response = session.get(url)
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

    except:
        print("Error scanning:", url)


# -------- SCAN ALL URLS --------
for url in urls:
    extract_forms(url)

# -------- REMOVE DUPLICATES --------
unique_forms = []
seen = set()

for form in forms_data:
    key = json.dumps(form, sort_keys=True)

    if key not in seen:
        seen.add(key)
        unique_forms.append(form)

# -------- SAVE TO FILE --------
with open("forms.json", "w") as f:
    json.dump(unique_forms, f, indent=4)

print("Forms saved to forms.json")