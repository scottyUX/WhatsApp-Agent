from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, ModelSettings, Runner, ItemHelpers

from app.config.settings import settings


image_agent = Agent(
    name="ImageExplainAgent",
    instructions="""Assume that you are a hair transplant doctor.
    There is an image which shows the top of a person's head.
    Your task is to decide how many hair grafts are needed for a hair transplant.
    """,
    model=settings.IMAGE_AGENT_MODEL,
    model_settings=ModelSettings(
        temperature=settings.IMAGE_AGENT_TEMPERATURE,
        max_tokens=settings.IMAGE_AGENT_MAX_TOKENS
    ),
)

async def run_image_agent(user_input: str, image_urls: list) -> str:
    print("🗣️ Image agent activated")
    content = [{"type": "input_text", "text": user_input}]
    content += [{"type": "input_image", "image_url": url} for url in image_urls]
    result = await Runner.run(image_agent,
        input=[
            {
                "role": "user",
                "content": content
            }
        ]
    )
    return result.final_output or "Sorry, I couldn't find an answer."


async def run_image_agent_streaming(user_input: str, image_urls: list):
    """Stream the image agent response for real-time output"""
    print("🗣️ Image agent activated (streaming)")
    content = [{"type": "input_text", "text": user_input}]
    content += [{"type": "input_image", "image_url": url} for url in image_urls]
    input = [
        {
            "role": "user",
            "content": content
        }
    ]
    result = Runner.run_streamed(image_agent, input=input)
    async for event in result.stream_events():
        # Raw response tokens from the LLM
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
            yield event.data.delta

        # Higher level events: message output, tool calls, etc
        elif event.type == "run_item_stream_event":
            name = event.name  # e.g. 'tool_called', 'tool_output', 'message_output_created'
            item = event.item
            if name == "tool_called":
                # tool was called
                pass
            elif name == "tool_output":
                # tool output received
                pass
            elif name == "message_output_created":
                # the difference between this and raw response is that this is higher level, after tool calls etc
                text = ItemHelpers.text_message_output(item)
                pass

        # If the agent is switching (handoff) to another agent
        elif event.type == "agent_updated_stream_event":
            # agent switched
            pass

    # Once done
    print("\n=== Streaming complete ===")
