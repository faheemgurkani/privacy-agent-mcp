import re



def redact_with_regex(text):
    text = re.sub(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b", "[REDACTED_NAME]", text)
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)
    text = re.sub(r"[\w.-]+@[\w.-]+", "[REDACTED_EMAIL]", text)
    
    return text

def extract_pii_fields(text):
    return {
        "names": re.findall(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b", text),
        "ssn": re.findall(r"\b\d{3}-\d{2}-\d{4}\b", text),
        "emails": re.findall(r"[\w.-]+@[\w.-]+", text),
    }

def redact_pii(text: str) -> dict:
    """
    Redacts PII from input text using regex.
    """
    redacted_text = redact_with_regex(text)
    pii_info = extract_pii_fields(text)
    
    return {"redacted_text": redacted_text, "pii_found": pii_info}



if __name__ == "__main__":
    # print(redact_pii("John is a good boy"))
    print(redact_pii("John Smith is a good boy. His SSN is 123-45-6789 and email is john.smith@example.com."))

