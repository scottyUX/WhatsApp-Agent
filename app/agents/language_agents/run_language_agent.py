from typing import AsyncGenerator
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, RunResult, ItemHelpers


async def run_agent(agent: Agent, user_input: str) -> str:
    print(f"{agent.name} activated")
    result: RunResult = await Runner.run(agent, user_input)
    return result.final_output or f"Sorry, I couldn't find an answer for {agent.name}."


async def run_agent_streaming(agent: Agent, user_input: str) -> AsyncGenerator[str, None]:
    """Stream the agent response for real-time output"""
    print(f"{agent.name} activated (streaming)")
    result = Runner.run_streamed(agent, user_input)
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
