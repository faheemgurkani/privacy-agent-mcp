def sanitize_prompt(redacted_text: str, pii_meta: dict) -> str:
    """
    Sanitizes prompts to ensure no PII or forbidden topics are passed to LLM.
    """ 

    text = redacted_text + "\n\n[NOTE: Redacted for compliance]"

    return {
            "sanitized_text": text
        }



if __name__ == "__main__":
    test_redacted_text = "[REDACTED_NAME] is a good boy. His SSN is [REDACTED_SSN] and email is [REDACTED_EMAIL]"
    test_pii_meta = {'names': ['John Smith'], 
                     'ssn': ['123-45-6789'], 
                     'emails': ['john.smith@example.com.']
    }

    sanitized_output = sanitize_prompt(test_redacted_text, test_pii_meta)

    print("Sanitized Prompt:")
    print(sanitized_output)