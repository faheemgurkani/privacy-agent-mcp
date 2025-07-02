from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import yaml
import os

from tools.redact_pii import redact_pii as redact_pii_fn
from tools.sanitize_prompt import sanitize_prompt as sanitize_prompt_fn
from tools.secure_memory import store_secure_memory as store_secure_memory_fn
from tools.audit_logger import log_audit as log_audit_fn

from pathlib import Path



load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

try:
    config_path = Path(__file__).resolve().parent / "resources" / "policy_config.yaml"

    # print(config_path)  # For, testing

    with open(config_path) as f:
        policy_config = yaml.safe_load(f)

except Exception as e:
    print("Failed to load YAML config:", e)

    exit(1)

mcp = FastMCP(name="PrivacyAwareMCP", host="0.0.0.0", port=8050)

# @mcp.tool()
# def redact_pii(text: str):
#     return redact_pii_fn(text)

# @mcp.tool()
# def sanitize_prompt(redacted_text: str, pii_meta: dict):
#     return sanitize_prompt_fn(redacted_text, pii_meta)

# @mcp.tool()
# def store_secure_memory(text: str, tags: list = None):
#     return store_secure_memory_fn(text, tags)

# @mcp.tool()
# def log_audit(event: dict):
#     return log_audit_fn(event)

# # # For, testing
# # @mcp.tool()
# # def redact_pii(text: str):
# #     print("✅ Tool loaded: redact_pii")
# #     return {"text": "[REDACTED]", "meta": {"dummy": True}}

# # @mcp.tool()
# # def sanitize_prompt(redacted_text: str, pii_meta: dict):
# #     print("✅ Tool loaded: sanitize_prompt")
# #     return {"sanitized_text": "sanitized version"}

# # @mcp.tool()
# # def store_secure_memory(text: str, tags: list = None):
# #     print("✅ Tool loaded: store_secure_memory")
# #     return {"status": "stored"}

# # @mcp.tool()
# # def log_audit(event: dict):
# #     print("✅ Tool loaded: log_audit")
# #     return {"status": "logged"}



# if __name__ == "__main__":
#     print("Starting FastMCP server via stdio")

#     try:
#         print("Running server with stdio transport")

#         mcp.run(transport="stdio")

#     except Exception as e:
        
#         import traceback
        
#         print("MCP server crashed:")
        
#         traceback.print_exc()

# For, testing
if __name__ == "__main__":
    import traceback
    import sys

    print("Starting FastMCP server via stdio", file=sys.stderr)
    try:
        print("[DEBUG] MCP instance created", file=sys.stderr)
        print("Registering tools...", file=sys.stderr)

        @mcp.tool()
        def redact_pii(text: str):
            print("Tool loaded: redact_pii")
            return redact_pii_fn(text)

        @mcp.tool()
        def sanitize_prompt(redacted_text: str, pii_meta: dict):
            print("Tool loaded: sanitize_prompt")
            
            return sanitize_prompt_fn(redacted_text, pii_meta)

        @mcp.tool()
        def store_secure_memory(text: str, tags: list = None):
            print("Tool loaded: store_secure_memory")
            
            return store_secure_memory_fn(text, tags)

        @mcp.tool()
        def log_audit(event: dict):
            print("Tool loaded: log_audit")
            
            return log_audit_fn(event)

        print("[DEBUG] About to run MCP server via stdio...", file=sys.stderr)
        mcp.run(transport="stdio")

    except Exception as e:
        print("MCP server crashed:")
        
        traceback.print_exc()

