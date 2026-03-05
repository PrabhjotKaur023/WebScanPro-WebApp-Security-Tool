import requests
import json

# DVWA base URL
BASE = "http://localhost:8080"

session = requests.Session()

# Common SQL error indicators
SQL_ERRORS = [
    "SQL syntax",
    "mysql_fetch",
    "syntax error",
    "Warning: mysql",
    "Unclosed quotation mark",
    "quoted string not properly terminated"
]


# ---------- LOAD FORMS ----------
def load_forms():
    with open("forms.json", "r") as f:
        return json.load(f)


# ---------- LOAD PAYLOADS ----------
def load_payloads():
    with open("payloads.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]


# ---------- CHECK SQL ERROR ----------
def is_sqli_vulnerable(response_text):

    for error in SQL_ERRORS:
        if error.lower() in response_text.lower():
            return True

    return False


# ---------- TEST FORM ----------
def test_form(form, payloads):

    url = form["action"]
    method = form["method"]
    inputs = form["inputs"]

    print("\nTesting form on:", form["page"])

    for payload in payloads:

        data = {}

        for inp in inputs:

            name = inp["name"]

            if name is None:
                continue

            # inject payload into text inputs
            if inp["type"] in ["text", "password"]:
                data[name] = payload
            else:
                data[name] = "test"

        try:

            if method == "post":
                res = session.post(url, data=data)

            else:
                res = session.get(url, params=data)

            if is_sqli_vulnerable(res.text):

                print("🚨 SQL Injection Found!")
                print("URL:", url)
                print("Payload:", payload)
                print("Data Sent:", data)

                return

        except Exception as e:
            print("Request error:", e)


# ---------- MAIN ----------
def main():

    forms = load_forms()
    payloads = load_payloads()

    print("Total forms loaded:", len(forms))
    print("Total payloads:", len(payloads))

    for form in forms:
        test_form(form, payloads)


main()