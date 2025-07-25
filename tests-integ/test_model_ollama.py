import pytest
import requests
from pydantic import BaseModel

import strands
from strands import Agent
from strands.models.ollama import OllamaModel


def is_server_available() -> bool:
    try:
        return requests.get("http://localhost:11434").ok
    except requests.exceptions.ConnectionError:
        return False


@pytest.fixture(scope="module")
def model():
    return OllamaModel(host="http://localhost:11434", model_id="llama3.3:70b")


@pytest.fixture(scope="module")
def tools():
    @strands.tool
    def tool_time() -> str:
        return "12:00"

    @strands.tool
    def tool_weather() -> str:
        return "sunny"

    return [tool_time, tool_weather]


@pytest.fixture(scope="module")
def agent(model, tools):
    return Agent(model=model, tools=tools)


@pytest.fixture(scope="module")
def weather():
    class Weather(BaseModel):
        """Extracts the time and weather from the user's message with the exact strings."""

        time: str
        weather: str

    return Weather(time="12:00", weather="sunny")


@pytest.mark.skipif(not is_server_available(), reason="Local Ollama endpoint not available at localhost:11434")
def test_agent_invoke(agent):
    result = agent("What is the time and weather in New York?")
    text = result.message["content"][0]["text"].lower()

    assert all(string in text for string in ["12:00", "sunny"])


@pytest.mark.skipif(not is_server_available(), reason="Local Ollama endpoint not available at localhost:11434")
@pytest.mark.asyncio
async def test_agent_invoke_async(agent):
    result = await agent.invoke_async("What is the time and weather in New York?")
    text = result.message["content"][0]["text"].lower()

    assert all(string in text for string in ["12:00", "sunny"])


@pytest.mark.skipif(not is_server_available(), reason="Local Ollama endpoint not available at localhost:11434")
@pytest.mark.asyncio
async def test_agent_stream_async(agent):
    stream = agent.stream_async("What is the time and weather in New York?")
    async for event in stream:
        _ = event

    result = event["result"]
    text = result.message["content"][0]["text"].lower()

    assert all(string in text for string in ["12:00", "sunny"])


@pytest.mark.skipif(not is_server_available(), reason="Local Ollama endpoint not available at localhost:11434")
def test_agent_structured_output(agent, weather):
    tru_weather = agent.structured_output(type(weather), "The time is 12:00 and the weather is sunny")
    exp_weather = weather
    assert tru_weather == exp_weather


@pytest.mark.skipif(not is_server_available(), reason="Local Ollama endpoint not available at localhost:11434")
@pytest.mark.asyncio
async def test_agent_structured_output_async(agent, weather):
    tru_weather = await agent.structured_output_async(type(weather), "The time is 12:00 and the weather is sunny")
    exp_weather = weather
    assert tru_weather == exp_weather
