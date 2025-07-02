import asyncio
import json
import traceback
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional
from pathlib import Path

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
import sys



nest_asyncio.apply()

# Loading .env from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

class MCPOpenAIClient:

    def __init__(self, model: str = "gpt-4o"):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai_client = AsyncOpenAI()
        self.model = model
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None

    async def connect_to_server(self, server_script_path: str = "server.py"):
        
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                stderr_to_stdout=True
            )

            print("[DEBUG] Launching server subprocess...")
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )

            # await asyncio.sleep(35)   # For, testing

            print("[DEBUG] Server subprocess launched successfully.")

            self.stdio, self.write = stdio_transport

            # print(self.stdio)   # For, testing
            # print(self.write)

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            print("Waiting for MCP server to be ready...")

            # Try initializing with retries (e.g., for up to 5 seconds)
            for attempt in range(15):
                
                try:
                    await self.session.initialize()
                
                    print("Session Initialized")
                
                    break
                
                except Exception as init_err:
                    print(f"Initialization attempt {attempt + 1} failed: {init_err}")
                
                    await asyncio.sleep(5)
            else:
                raise RuntimeError("MCP server failed to initialize after retries.")

            tools_result = await self.session.list_tools()

            print("Connected to MCP server. Tools available:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

        except Exception as e:
            print(f"Failed to connect or initialize session: {e}")
            
            traceback.print_exc()
            
            await self.cleanup()
            
            return

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        
        try:
            tools_result = await self.session.list_tools()
        
            return [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in tools_result.tools
            ]
        
        except Exception as e:
            print(f"Failed to fetch MCP tools: {e}")
        
            traceback.print_exc()
        
            return []

    # async def process_query(self, query: str) -> str:
        
    #     try:
    #         tools = await self.get_mcp_tools()
        
    #         if not tools:
    #             raise RuntimeError("No tools loaded from server.")

    #         response = await self.openai_client.chat.completions.create(
    #             model=self.model,
    #             messages=[{"role": "user", "content": query}],
    #             tools=tools,
    #             tool_choice="auto",
    #         )
            
    #         assistant_message = response.choices[0].message
    #         messages = [{"role": "user", "content": query}, assistant_message]

    #         # For, testing
    #         print("\nTool calls requested by OpenAI:")
    #         for tc in assistant_message.tool_calls:
    #             print(f"🔹 {tc.function.name} with args: {tc.function.arguments}")

    #         if assistant_message.tool_calls:
            
    #             for tool_call in assistant_message.tool_calls:
    #                 result = await self.session.call_tool(
    #                     tool_call.function.name,
    #                     arguments=json.loads(tool_call.function.arguments),
    #                 )
            
    #                 tool_result_dict = result.content[0].text

    #                 # For, testing
    #                 print(f"\nTool '{tool_call.function.name}' returned:\n{json.dumps(tool_result_dict, indent=2)}")

    #                 messages.append({
    #                     "role": "tool",
    #                     "tool_call_id": tool_call.id,
    #                     "content": json.dumps(tool_result_dict),  
    #                 })

    #             final_response = await self.openai_client.chat.completions.create(
    #                 model=self.model,
    #                 messages=messages,
    #                 tools=tools,
    #                 tool_choice="none",
    #             )
            
    #             return final_response.choices[0].message.content

    #         return assistant_message.content

    #     except Exception as e:
    #         print(f"Error during query processing: {e}")
            
    #         traceback.print_exc()
            
    #         return "Error occurred during query processing."
    async def process_query(self, query: str) -> str:
        
        try:
            tools = await self.get_mcp_tools()
        
            if not tools:
                raise RuntimeError("No tools loaded from server.")

            # Step 1: Asking OpenAI to call redact_pii if needed
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": query}],
                tools=tools,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message
            messages = [{"role": "user", "content": query}, assistant_message]

            pii_result = None
            sanitized_result = None

            if assistant_message.tool_calls:
        
                for tool_call in assistant_message.tool_calls:
        
                    if tool_call.function.name == "redact_pii":
                        redact_result = await self.session.call_tool(
                            tool_call.function.name,
                            arguments=json.loads(tool_call.function.arguments),
                        )
        
                        redact_data = json.loads(redact_result.content[0].text)

                        pii_result = redact_data
        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(redact_data),
                        })

                        # Step 2: Calling sanitize_prompt manually
                        sanitize_args = {
                            "redacted_text": redact_data["redacted_text"],
                            "pii_meta": redact_data["pii_found"],
                        }
        
                        sanitize_result = await self.session.call_tool(
                            "sanitize_prompt", arguments=sanitize_args
                        )
        
                        sanitized_result = sanitize_result.content[0].text

            # Step 3: Querying LLM with sanitized input if PII was found
            final_query = sanitized_result if sanitized_result else query

            print()
            print(f"Redacted query: {final_query['sanitized_text']}")

            final_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": final_query}],
            )

            return final_response.choices[0].message.content

        except Exception as e:
            print(f"❌ Error during query processing: {e}")
            
            traceback.print_exc()
            
            return "Error occurred during query processing."

    # async def cleanup(self):
    #     try:
    #         await self.exit_stack.aclose()
        
    #     except Exception as e:
    #         print(f"Error during cleanup: {e}")
        
    #         traceback.print_exc()
    async def cleanup(self):

        try:

            if self.exit_stack:
                await self.exit_stack.aclose()

            print("[INFO] Client and server cleaned up successfully.")

            return 

        except Exception as e:
            print(f"[ERROR] Error during cleanup: {e}")

            traceback.print_exc()



async def main():
    client = MCPOpenAIClient()
    
    await client.connect_to_server("server.py")

    if client.session is None:
        print("Client session was not established. Exiting.")
    
        return

    query = "John Smith is a good boy. His SSN is 123-45-6789 and email is john.smith@example.com. What should he do to avoid getting used by others?"
    # Like his name is getting used every, dragging through dirt of various programs

    print(f"\nQuery: {query}")

    response = await client.process_query(query)

    print(f"\nResponse: {response}")

    await client.cleanup()



if __name__ == "__main__":
    asyncio.run(main())

    import sys

    sys.exit(0) 
