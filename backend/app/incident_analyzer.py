from collections import Counter


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

Your job is to identify plausible explanations based ONLY on the supplied log evidence.
Do not claim certainty when the logs do not prove a root cause.

Incident summary:
Total logs: {len(logs)}
Log levels: {dict(levels)}
Services involved: {dict(services)}

Relevant logs:
{formatted_logs}

Return an incident analysis containing:

1. Likely cause
2. Evidence from the logs
3. Affected services
4. Recommended debugging checks
5. Confidence level

Clearly distinguish observed evidence from hypotheses.
""".strip()