import json
import os
import re

from dotenv import load_dotenv
from google import genai


# Load variables from .env
load_dotenv()


# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def extract(raw_text: str) -> dict:

    prompt = f"""
You are an AI system that extracts structured information
from citizen problem submissions.

Analyze the citizen's complaint and return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations outside the JSON.

The JSON must contain these fields:

{{
    "domain": "",
    "subdomain": "",
    "problem": "",
    "severity": "",
    "urgency": "",
    "affected_population": "",
    "keywords": [],
    "required_capabilities": [],
    "potential_causes": [],
    "confidence": 0.0,
    "reason": ""
}}

Rules:

1. domain should be the broad problem area.
   Examples:
   water, education, healthcare, sanitation,
   agriculture, roads, environment, employment

2. subdomain should be more specific.

3. problem should be a short, clear description
   of the actual problem.

4. severity must be one of:
   low, medium, high, critical

5. urgency must be one of:
   low, medium, high, critical

6. affected_population should describe who is affected.

7. keywords should contain important words or phrases
   from the complaint.

8. required_capabilities should contain skills,
   technologies, departments, or expertise that may
   be required to solve the problem.

9. potential_causes should contain possible causes.
   Do not present guesses as confirmed facts.

10. confidence must be a number between 0 and 1.

11. reason should briefly explain why you selected
    the domain, severity and confidence.

12. If the complaint is vague or there is not enough
    information, reduce the confidence score.

Citizen complaint:

{raw_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        result = response.text

        # Remove unnecessary spaces
        result = result.strip()

        # Remove markdown fences if Gemini somehow adds them
        result = re.sub(r"^```json\s*", "", result)
        result = re.sub(r"^```\s*", "", result)
        result = re.sub(r"\s*```$", "", result)

        # Convert JSON string into Python dictionary
        data = json.loads(result)

        # Check confidence
        confidence = data.get("confidence", 0)

        if confidence < 0.70:
            data["human_verification_required"] = True
        else:
            data["human_verification_required"] = False

        return data

    except Exception as e:

        return {
            "error": "Extraction failed",
            "message": str(e)
        }


# Test the function
if __name__ == "__main__":

    complaint = """
    A water supply pipe has been leaking continuously near
    the Main Market road, causing water wastage and making
    the road muddy.
    """

    result = extract(complaint)

    print(json.dumps(result, indent=2))