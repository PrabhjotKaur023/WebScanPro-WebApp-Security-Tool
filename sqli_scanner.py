import requests
import json

session = requests.Session()

# -------- LOAD FILES --------
with open("urls.json", "r") as f:
    urls = json.load(f)

with open("forms.json", "r") as f:
    forms = json.load(f)

with open("payloads.txt", "r") as f:
    payloads = [line.strip() for line in f if line.strip()]

vulnerabilities = []

# -------- SQL ERROR PATTERNS --------
errors = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "mysql_fetch",
    "mysql_num_rows",
    "sql syntax",
    "database error"
]

print("Starting SQL Injection Scan...\n")

# -------- SCAN URL PARAMETERS --------
for url in urls:

    print("Scanning URL:", url)

    for payload in payloads:

        try:
            test_url = url + "?id=" + payload
            res = session.get(test_url)

            content = res.text.lower()

            for error in errors:

                if error in content:

                    print("SQL Injection Found in URL!")
                    print("URL:", test_url)
                    print()

                    vulnerabilities.append({
                        "type": "SQL Injection",
                        "url": test_url,
                        "payload": payload
                    })

                    break

        except:
            continue


# -------- SCAN FORMS --------
for form in forms:

    action = form["action"]
    method = form["method"]
    inputs = form["inputs"]

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

            for error in errors:

                if error in content:

                    print("SQL Injection Found in Form!")
                    print("URL:", action)
                    print("Payload:", payload)
                    print()

                    vulnerabilities.append({
                        "type": "SQL Injection",
                        "url": action,
                        "payload": payload
                    })

                    break

        except:
            continue


# -------- SAVE RESULTS --------
with open("vulnerabilities.json", "w") as f:
    json.dump(vulnerabilities, f, indent=4)

print("\nScan Completed")