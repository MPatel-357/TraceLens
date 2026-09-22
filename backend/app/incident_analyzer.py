from collections import Counter
import json

from openai import OpenAI

client = OpenAI()


def build_incident_prompt(logs: list[dict]) -> str:
    if not logs:
        return "No logs were provided for this incident."

    levels = Counter(log["level"] for log in logs)
    services = Counter(log["service"] for log in logs)

    formatted_logs = "\n".join(
        f"[{log['timestamp']}] "
        f"{log['level']} "
        f"{log['service']}: "
        f"{log['message']}"
        for log in logs
    )

    return f"""
You are analyzing an application incident detected by an anomaly-detection system.

Analyze the incident using ONLY the supplied log evidence.

Do not invent infrastructure details.
Do not claim certainty when the logs do not prove the root cause.
Clearly distinguish observations from hypotheses.

Incident summary:
Total logs: {len(logs)}
Log levels: {dict(levels)}
Services involved: {dict(services)}

Relevant logs:
{formatted_logs}

Return ONLY valid JSON with this structure:

{{
    "summary": "brief incident summary",
    "likely_cause": "most plausible explanation based on the evidence",
    "evidence": [
        "specific observation from the logs"
    ],
    "affected_services": [
        "service name"
    ],
    "recommended_checks": [
        "specific debugging step"
    ],
    "confidence": "low, medium, or high"
}}
""".strip()


def analyze_incident(logs: list[dict]) -> dict:
    prompt = build_incident_prompt(logs)

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    output = response.output_text.strip()

    if output.startswith("```"):
        output = output.removeprefix("```json")
        output = output.removeprefix("```")
        output = output.removesuffix("```")
        output = output.strip()

    return json.loads(output)