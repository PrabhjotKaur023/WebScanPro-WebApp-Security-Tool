🔐 WebScanPro – Web Application Security Testing Tool

🚧 Project Status: Currently in Development

WebScanPro is an automated Web Application Security Testing Tool designed to identify vulnerabilities in web applications. The tool scans websites, extracts forms and URLs, and tests them with security payloads to detect potential vulnerabilities such as SQL Injection.

This project is being developed as part of the Infosys Internship Program, where the focus is on applying automation, data analysis, and cybersecurity concepts to build a practical security testing solution.

🎯 Project Goals

Develop an automated tool to scan web applications for vulnerabilities

Extract URLs and forms from websites for security testing

Test input fields with security payloads

Analyze server responses to detect possible vulnerabilities

Store and organize scan results for further analysis

⚙️ How the Tool Works

The system follows these steps:

1️⃣ Website Crawling
Collects internal links from the target website.

2️⃣ Form Extraction
Detects HTML forms and identifies input fields.

3️⃣ Payload Injection
Sends specially crafted payloads to test form inputs.

4️⃣ Response Analysis
Analyzes responses to detect possible vulnerabilities.

5️⃣ Report Generation
Stores results in structured files for security reporting.

🧩 Project Modules
🌐 URL Crawler

Crawls the target website

Collects internal URLs

Stores results in urls.json

📝 Form Extractor

Detects and extracts HTML forms

Collects form attributes and input fields

Stores extracted data in forms.json

💉 SQL Injection Scanner

Sends SQL payloads to form inputs

Analyzes responses for database error patterns

📊 Vulnerability Reporter

Stores detected vulnerabilities

Generates reports in vulnerabilities.json

🛠️ Technologies Used

Python

Requests Library

BeautifulSoup

JSON for Data Storage

Web Security Testing Concepts

📂 Project Structure
WebScanPro
│
├── crawler.py
├── form_extractor.py
├── sqli_scanner.py
├── urls.json
├── forms.json
├── vulnerabilities.json
└── README.md
📚 Learning Outcomes

Through this internship project, I am developing skills in:

Web application security testing

Python automation scripting

Data collection and analysis

Vulnerability detection techniques

Practical cybersecurity concepts

🚀 Future Enhancements

Add Cross-Site Scripting (XSS) detection

Improve vulnerability detection accuracy

Build a web dashboard for scan results

Implement advanced automated security testing
