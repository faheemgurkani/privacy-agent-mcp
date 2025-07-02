# Privacy-Aware Agent MCP System

This project implements a privacy-aware multi-step workflow using the Model Context Protocol (MCP) architecture, combining tool-based reasoning with language model capabilities to securely process sensitive user queries.

## Overview

The system is designed to:

1. Detect and redact personally identifiable information (PII).
2. Sanitize redacted content for further safe processing.
3. Store redacted and sanitized content in a secure memory.
4. Log audit trails for accountability.
5. Send the sanitized query to an LLM for final answer generation.

## Architecture

```
User Query
   |
   v
[Client]
   |
   |---> [Tool Call 1] redact_pii
   |         |
   |         v
   |     redacted_text + pii_found
   |
   |---> [Tool Call 2] sanitize_prompt (invoked automatically)
   |         |
   |         v
   |     sanitized_text
   |
   |---> [Final Step] LLM Query using sanitized_text
   v
[Response Returned to User]
```

## Components

### 1. **Client (client.py)**

The entrypoint for processing user queries. Responsibilities:

* Establishes a session with the MCP server over stdio.
* Sends the user query to the LLM.
* Triggers the `redact_pii` tool based on LLM function calls.
* Automatically invokes `sanitize_prompt` after `redact_pii`.
* Feeds the sanitized text back into the LLM to generate the final answer.

### 2. **Server (server.py)**

The MCP server registers and runs the following tools:

* `redact_pii`: Redacts PII such as names, emails, SSNs.
* `sanitize_prompt`: Cleans up redacted content into a form suitable for downstream use.
* `store_secure_memory`: Persists sanitized data with tags for future reference.
* `log_audit`: Tracks each action performed for traceability.

### 3. **Tool Modules (tools/)**

Each tool function is implemented in its own Python module for modularity and reuse. These are used by the server to perform redaction, sanitization, secure storage, and logging.

### 4. **LLM Integration**

The `openai.AsyncOpenAI` client is used for all LLM-related processing. The model (e.g., `gpt-4o`) is configured to:

* Accept tool definitions.
* Choose when to invoke a tool.
* Resume conversation using sanitized text if PII is found.

## Workflow Logic

1. **Initial Tool Discovery**: Upon startup, the client lists all registered tools from the server.
2. **Initial Query Analysis**: The client sends the raw query to OpenAI with tool calling enabled (`tool_choice="auto"`).
3. **Tool Call - Redaction**: If PII is detected, the LLM requests the `redact_pii` tool to be run.
4. **Tool Call - Sanitization**: The client automatically invokes the `sanitize_prompt` tool using the output from the redaction step.
5. **LLM Final Answer**: The sanitized query is then submitted to the LLM to generate a safe response.
6. **Tool Chaining Support**: This pattern can be extended further by chaining other tools (e.g., logging or secure memory).

## Environment

* Python 3.12+
* OpenAI Python SDK
* MCP SDK (`mcp`, `fastmcp`)
* dotenv

## Running the System

From the root of the project:

```bash
python src/client.py
```

This will automatically launch the server via subprocess (`server.py`) and process the input query according to the workflow.

## Notes

* The `sanitize_prompt` tool is always invoked client-side immediately after `redact_pii`.
* The final response is always generated using a sanitized version of the original input.
* All communication with the server is via `stdio` transport to enforce separation of execution and ensure data privacy.

## Extending

To further enhance the system:

* Introduce policy-based enforcement of tool order on the server.
* Add encrypted secure memory or zero-trust logging.
* Integrate with external compliance APIs.

## License

This project is open-sourced under the MIT license.
