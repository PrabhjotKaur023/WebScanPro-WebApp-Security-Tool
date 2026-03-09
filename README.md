# 🔐 WebScanPro – Web Application Security Testing Tool

🚧 **Project Status:** Currently in Development  

WebScanPro is an automated **Web Application Security Testing Tool** designed to identify common vulnerabilities in web applications. The tool scans websites, extracts forms and URLs, and tests them using security payloads to detect vulnerabilities such as **SQL Injection**.

This project is being developed as part of the **Infosys Internship Program**, where the focus is on applying **automation, data analysis, and cybersecurity concepts** to build a practical security testing solution.

---

## 🎯 Project Goals

- Develop an automated tool to **scan web applications for vulnerabilities**
- Extract **URLs and forms** from websites for testing
- Analyze server responses to detect suspicious behavior
- Store results in structured formats for reporting
- Improve security testing efficiency through automation

---

## ⚙️ How WebScanPro Works

The tool follows these steps:

1. **Website Crawling**  
   Collects internal links from the target website.

2. **Form Extraction**  
   Detects HTML forms and identifies input fields.

3. **Payload Injection**  
   Sends specially crafted payloads to form inputs to test vulnerabilities.

4. **Response Analysis**  
   Analyzes server responses to detect database errors or suspicious patterns.

5. **Report Generation**  
   Stores detected vulnerabilities in structured files.

---

## 🧩 Project Modules

### 🌐 URL Crawler
- Crawls the target website
- Collects internal URLs
- Saves results in `urls.json`

### 📝 Form Extractor
- Detects and extracts HTML forms
- Captures form actions, methods, and input fields
- Stores extracted data in `forms.json`

### 💉 SQL Injection Scanner
- Sends SQL payloads to input fields
- Analyzes responses for database error patterns
- Detects possible SQL Injection vulnerabilities

### 📊 Vulnerability Reporter
- Stores detected vulnerabilities
- Generates reports in `vulnerabilities.json`

---

## 🛠️ Technologies Used

- **Python**
- **Requests Library**
- **BeautifulSoup**
- **JSON for Data Storage**
- **Web Security Testing Concepts**

---

## 📂 Project Structure
WebScanPro
│
├── crawler.py
├── form_extractor.py
├── sqli_scanner.py
├── urls.json
├── forms.json
├── vulnerabilities.json
└── README.md


---

## 📚 Learning Outcomes

Through this internship project, I am developing skills in:

- Web application security testing  
- Python automation scripting  
- Web scraping and data collection  
- Vulnerability detection techniques  
- Practical cybersecurity concepts  

---

## 🚀 Future Enhancements

- Add **Cross-Site Scripting (XSS) detection**
- Improve vulnerability detection accuracy
- Build a **dashboard for vulnerability reports**
- Implement **advanced automated security testing**

---

👨‍💻 **Developed as part of the Infosys Internship Program**
