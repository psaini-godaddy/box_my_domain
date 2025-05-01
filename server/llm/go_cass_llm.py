import requests
from urllib.parse import urljoin
from llm.prompt_formatter import build_plan_prompt, build_update_prompt
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class GoCaas:
    def __init__(self, host_url="https://caas.api.dev-godaddy.com", path="v1/prompts"):
        self.url = urljoin(host_url, path)

    def call(self, token: str, prompt: str) -> str:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"sso-jwt {token}"
        }
        data = {
            "prompt": prompt,
            "provider": "openai_chat",
            "providerOptions": {
                "max_tokens": 16384,
                "temperature": 0.6,
                "top_p": 0.8,
                "model": "gpt-4o"
            }
        }

        print(f"[GoCaas] 🔁 Sending prompt to {self.url}...")
        response = requests.post(self.url, json=data, headers=headers)
        response.raise_for_status()

        print("[GoCaas] ✅ Response received.")
        return response.json()['data']['value']

    def generate_plan(self, token: str, objective: str, tool_metadata: list) -> list:
        """
        High-level wrapper: builds plan prompt, sends to LLM, returns parsed plan (list of steps).

        :param token: API auth token
        :param objective: user's original prompt
        :param tool_metadata: list of available tools and their schemas
        :return: list of plan steps
        """
        prompt = build_plan_prompt(objective, tool_metadata)
        raw_output = self.call(token, prompt)
        return self._parse_plan_response(raw_output)

    def generate_updated_plan(self, token: str, original_plan: dict, feedback: dict, executed_steps: list,
                              tool_metadata: list) -> list:
        prompt = build_update_prompt(original_plan, feedback, executed_steps, tool_metadata)
        print(f"[GoCaas] 🧠 Generating updated plan with feedback...")
        print("[GoCaas] 🔍 Prompt for updated plan:")
        print(prompt)
        raw_output = self.call(token, prompt)
        return self._parse_plan_response(raw_output)

    def _parse_plan_response(self, raw_text: str) -> list:
        """
        Parses the raw LLM output into a list of action dictionaries.
        Assumes it's a JSON array.
        """
        try:
            print("[GoCaas] 🧠 Parsing LLM response...")
            raw_text = raw_text.replace("```json", "")
            raw_text = raw_text.replace("```", "")  # Remove any code block markers
            parsed = json.loads(raw_text.strip())
            assert isinstance(parsed, list), "Expected JSON array"
            return parsed
        except Exception as e:
            print(f"[GoCaas] ❌ Failed to parse LLM output: {e}")
            print("LLM raw output:", raw_text)
            return []


if __name__ == "__main__":
    from token_manager import TokenManager

    sample_prompt = "You are a helpful assistant. Say hello to the user."
    caas = GoCaas()

    try:
        print("🔐 Fetching token from TokenManager...")
        token = TokenManager().token

        print("🚀 Sending sample prompt to GoCaaS...")
        response = caas.call(token, sample_prompt)

        print("🎉 LLM Response:")
        print(response)
    except Exception as e:
        print(f"❌ Test failed: {e}")