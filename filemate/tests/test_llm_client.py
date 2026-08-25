from filemate.llm_client.client import LLMClient
from filemate.llm_client.config import LLMConfig
from filemate.llm_client.providers.step_speed import StepSpeedProvider


def test_deepseek_base_url_uses_openai_compatible_provider() -> None:
    config = LLMConfig(
        provider="auto",
        api_key="sk-test",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-v4-pro",
    )
    provider = LLMClient._build(config)
    assert isinstance(provider, StepSpeedProvider)
