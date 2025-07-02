import json



def log_audit(event: dict) -> str:
    """
    Logs interaction metadata for traceability and compliance.
    """
    with open("audit.log", "a") as logf:
        logf.write(json.dumps(event) + "\n")

    return "Logged"
