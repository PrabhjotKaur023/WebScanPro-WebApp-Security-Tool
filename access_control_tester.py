"""
WebScanPro - Access Control & IDOR Testing Module
"""

import requests
import json
import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup


# ---------- LOGIN ----------
def login_dvwa(base_url, login_url, username="admin", password="password"):

    session = requests.Session()

    try:
        res = session.get(login_url)

        soup = BeautifulSoup(res.text, "html.parser")
        token = soup.find("input", {"name": "user_token"})
        token_value = token["value"] if token else ""

        data = {
            "username": username,
            "password": password,
            "Login": "Login",
            "user_token": token_value
        }

        login_res = session.post(login_url, data=data)

        if "login.php" not in login_res.url:
            print("[+] Login successful")
            session.cookies.set("security", "low")
            return session
        else:
            print("[-] Login failed")
            return None

    except Exception as e:
        print("[-] Login error:", e)
        return None


# ---------- BROKEN ACCESS CONTROL ----------
def test_broken_access_control(url):

    unauth_session = requests.Session()

    try:
        res = unauth_session.get(url, allow_redirects=True)

        if res.status_code == 200 and "login.php" not in res.url:

            print(f"[!!!] Broken Access Found: {url}")

            return {
                "url": url,
                "vulnerability_type": "Broken Access Control",
                "description": "Page is accessible without authentication.",
                "remediation": "Implement proper session validation on all restricted endpoints."
            }

    except requests.RequestException:
        pass

    return None


# ---------- IDOR ----------
def test_idor(url, form, session):

    vulnerabilities = []

    action = urljoin(url, form.get("action")) if form.get("action") else url
    method = form.get("method", "get").lower()
    inputs = form.get("inputs", [])

    idor_targets = ["id", "user", "uid", "account"]

    for input_field in inputs:

        name = input_field.get("name")

        if not name:
            continue

        if name.lower() in idor_targets:

            print(f"[+] IDOR target parameter found: {name}")

            responses = []

            # Try IDs 1, 2, 3
            for test_id in ["1", "2", "3"]:

                data = {}

                for inp in inputs:
                    inp_name = inp.get("name")

                    if not inp_name:
                        continue

                    if inp_name == name:
                        data[inp_name] = test_id
                    elif inp.get("type") == "submit":
                        data[inp_name] = "Submit"
                    else:
                        data[inp_name] = inp.get("value", "")

                try:
                    if method == "post":
                        res = session.post(action, data=data)
                    else:
                        res = session.get(action, params=data)

                    responses.append(len(res.text))

                except requests.RequestException:
                    continue

            # 🔥 CORE LOGIC
            if len(set(responses)) > 1:

                print(f"[!!!] IDOR Found: Parameter '{name}'")

                vulnerabilities.append({
                    "url": action,
                    "vulnerability_type": "Insecure Direct Object Reference (IDOR)",
                    "vulnerable_input": name,
                    "description": f"Manipulating the '{name}' parameter returned unique data records.",
                    "remediation": "Implement access control checks to verify authorization."
                })

    return vulnerabilities


# ---------- MAIN ----------
def main():

    if len(sys.argv) < 3:
        print("Usage: python access_control_tester.py <base_url> <login_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    login_url = sys.argv[2]

    # ---------- LOAD URLS ----------
    try:
        with open("urls.json", "r") as f:
            urls = json.load(f)
    except FileNotFoundError:
        print("[-] urls.json not found")
        sys.exit(1)

    # ---------- LOAD FORMS ----------
    try:
        with open("forms.json", "r") as f:
            forms = json.load(f)
    except FileNotFoundError:
        print("[-] forms.json not found")
        sys.exit(1)

    print("\n[+] Starting Access Control & IDOR Tests...\n")

    all_vulnerabilities = []

    # ---------- BROKEN ACCESS ----------
    print("[+] Testing Broken Access Control...\n")

    for url in urls:
        if "login.php" in url:
            continue

        result = test_broken_access_control(url)

        if result:
            all_vulnerabilities.append(result)

    # ---------- LOGIN ----------
    print("\n[+] Logging in for IDOR tests...\n")

    session = login_dvwa(base_url, login_url)

    if not session:
        print("[-] Cannot continue without login")
        sys.exit(1)

    # ---------- IDOR ----------
    print("\n[+] Testing IDOR...\n")

    for form in forms:

        page = form.get("page")

        if not page:
            continue

        vulns = test_idor(page, form, session)

        all_vulnerabilities.extend(vulns)

    # ---------- SAVE ----------
    with open("access_control_vulnerabilities.json", "w") as f:
        json.dump(all_vulnerabilities, f, indent=4)

    print(f"\n[+] Scan Completed: {len(all_vulnerabilities)} vulnerabilities found")


# ---------- ENTRY ----------
if __name__ == "__main__":
    main()