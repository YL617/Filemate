from filemate.llm_client.client import LLMClient
from filemate.llm_client.config import LLMConfig
from filemate.llm_client.providers.step_speed import StepSpeedProvider


class _FakeResponse:
    status_code = 200

    @staticmethod
    def json() -> dict:
        return {"choices": [{"message": {"content": "OK"}}]}


def test_deepseek_base_url_uses_openai_compatible_provider() -> None:
    config = LLMConfig(
        provider="auto",
        api_key="sk-test",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-v4-pro",
    )
    provider = LLMClient._build(config)
    assert isinstance(provider, StepSpeedProvider)


def test_deepseek_disables_thinking(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_post(url: str, json: dict, headers: dict, timeout: float) -> _FakeResponse:
        captured["url"] = url
        captured["json"] = json
        return _FakeResponse()

    monkeypatch.setattr(
        "filemate.llm_client.providers.step_speed.requests.post",
        fake_post,
    )

    config = LLMConfig(
        provider="deepseek",
        api_key="sk-test",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-v4-pro",
    )
    provider = StepSpeedProvider(config)
    text = provider.chat(
        [{"role": "user", "content": "hi"}],
        max_tokens=32,
    )

    assert text == "OK"
    assert captured["url"] == "https://api.deepseek.com/v1/chat/completions"
    assert captured["json"]["thinking"] == {"type": "disabled"}
