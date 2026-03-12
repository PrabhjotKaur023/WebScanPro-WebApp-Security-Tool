import os
import json
from typing import Optional
from google import genai
from openai import OpenAI
from dotenv import load_dotenv

# Load .env variables
load_dotenv()


def summarize_text_with_gemini(text: str, max_length: int = 150) -> Optional[str]:

    if not text.strip():
        return "No text to summarize."

    # If input is a file
    if os.path.isfile(text):
        with open(text, "r", encoding="utf-8") as f:
            text = f.read()

    raw_text = text

    # Load API key from .env
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Correct Gemini model
    model = "gemini-2.0-flash"

    try:

        prompt = f"""
You are a cybersecurity expert.

Analyze the following vulnerability scan results and generate a short security report.

Include:
- Vulnerability type
- Affected URL
- Risk explanation
- Recommended fix

Limit the report to around {max_length} words.

Scan Results:
{raw_text}
"""

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        summary = response.text.strip()

        return summary if summary else "Summary generation failed."

    except Exception as e:
        return f"Error generating summary: {str(e)}"


def summarize_text_with_lm_studio(text: str, max_length: int = 150) -> Optional[str]:

    if not text.strip():
        return "No text to summarize."

    if os.path.isfile(text):
        with open(text, "r", encoding="utf-8") as f:
            text = f.read()

    raw_text = text

    client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:

        prompt = f"""
Summarize the following vulnerability scan results in {max_length} words:

{raw_text}
"""

        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": "You summarize security vulnerabilities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()

        return summary if summary else "Summary generation failed."

    except Exception as e:
        return f"Error generating summary: {str(e)}"


if __name__ == "__main__":

    try:

        # Load vulnerability scan results
        with open("vulnerabilities.json", "r") as f:
            vulnerabilities = json.load(f)

        if not vulnerabilities:
            print("No vulnerabilities found.")
            exit()

        text = json.dumps(vulnerabilities, indent=2)

        print("\nGemini AI Security Report:\n")

        result = summarize_text_with_gemini(text)

        print(result)

        # Save report
        with open("AI_Security_Report.txt", "w", encoding="utf-8") as f:
            f.write(result)

        print("\nReport saved to AI_Security_Report.txt")

    except FileNotFoundError:
        print("vulnerabilities.json not found.")