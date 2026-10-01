from typing import Callable, Awaitable, Dict, Any
from google import genai
from google.genai import types
from agent.client import get_genai_client
from agent.prompts import SYSTEM_PROMPT
from tools.registry import ALL_TOOLS, TOOL_MAP
from core.config import settings
from core.logger import logger

class Orchestrator:
    """Orchestrates Gemini LLM interaction, function calling execution, and real-time log broadcasting."""

    def __init__(self):
        self.client: genai.Client = None
        self.chat = None

    def _init_chat(self):
        if self.client is None:
            self.client = get_genai_client()

        if self.chat is None:
            self.chat = self.client.chats.create(
                model=settings.MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=ALL_TOOLS,
                    temperature=0.2,
                )
            )

    async def process_user_message(
        self,
        user_text: str,
        broadcast_func: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> str:
        """Process user text, handle Gemini tool calling loop, and broadcast progress to WebSocket."""
        logger.info(f"Orchestrator received prompt: '{user_text}'")

        await broadcast_func({
            "type": "user",
            "message": f"User: {user_text}"
        })

        await broadcast_func({
            "type": "status",
            "message": "🧠 Processing command with Gemini..."
        })

        try:
            self._init_chat()
            response = self.chat.send_message(user_text)

            max_tool_turns = 10
            turn = 0

            while response.function_calls and turn < max_tool_turns:
                turn += 1
                function_responses = []

                for call in response.function_calls:
                    func_name = call.name
                    func_args = call.args or {}

                    log_start_msg = f"Executing tool '{func_name}' with args {func_args}"
                    logger.info(log_start_msg)
                    await broadcast_func({
                        "type": "tool_start",
                        "tool": func_name,
                        "args": func_args,
                        "message": f"⚙️ {log_start_msg}"
                    })

                    tool_func = TOOL_MAP.get(func_name)
                    if tool_func:
                        try:
                            result = tool_func(**func_args)
                        except Exception as ex:
                            result = f"Error executing tool '{func_name}': {str(ex)}"
                    else:
                        result = f"Error: Tool '{func_name}' is not registered."

                    log_res_msg = f"Tool '{func_name}' output: {result}"
                    logger.info(log_res_msg)
                    await broadcast_func({
                        "type": "tool_end",
                        "tool": func_name,
                        "result": result,
                        "message": f"✅ {log_res_msg}"
                    })

                    function_responses.append(
                        types.Part.from_function_response(
                            name=func_name,
                            response={"result": result}
                        )
                    )

                response = self.chat.send_message(function_responses)

            final_text = response.text if response.text else "Command executed successfully."
            logger.info(f"Final Gemini response: {final_text}")

            await broadcast_func({
                "type": "response",
                "message": final_text
            })

            return final_text

        except Exception as e:
            err_msg = f"Error in Orchestrator: {str(e)}"
            logger.error(err_msg, exc_info=True)
            await broadcast_func({
                "type": "error",
                "message": err_msg
            })
            return err_msg

orchestrator = Orchestrator()
