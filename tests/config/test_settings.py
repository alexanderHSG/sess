from sess.config.settings import Settings


def test_settings_accept_env_aliases() -> None:
    settings = Settings(OpenAI="test-openai", LLAMA_CLOUD_API_KEY="test-llama", token="test-hf")
    assert settings.openai_api_key == "test-openai"
    assert settings.llama_cloud_api_key == "test-llama"
    assert settings.huggingface_token == "test-hf"

