"""Send a message to an OpenAI-compatible API and print the reply."""

import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent


def check_tools(client: OpenAI, model: str, options: dict) -> str:
    """Verify a real tool call, execute locally, then send the observation back."""
    tools = [{
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two integers using a local Python tool.",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
    }]
    messages = [{"role": "user", "content": "请调用 add_numbers 计算 2 + 3，再用中文告诉我结果。"}]
    response = client.chat.completions.create(
        model=model, messages=messages, tools=tools,
        tool_choice={"type": "function", "function": {"name": "add_numbers"}},
        **options,
    )
    message = response.choices[0].message
    if not message.tool_calls:
        raise ValueError("模型没有返回 tool_calls，Tool Calling 验收未通过。")
    messages.append(message.model_dump(exclude_none=True))
    for call in message.tool_calls:
        if call.type != "function" or call.function.name != "add_numbers":
            raise ValueError("模型请求了不支持的工具。")
        args = json.loads(call.function.arguments)
        if not isinstance(args, dict) or set(args) != {"a", "b"}:
            raise ValueError("工具参数应包含 a 和 b。")
        if any(type(args[name]) is not int for name in ("a", "b")):
            raise ValueError("工具参数必须是整数。")
        result = args["a"] + args["b"]
        print(f"工具调用：add_numbers({args['a']}, {args['b']}) → {result}")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
    response = client.chat.completions.create(model=model, messages=messages, **options)
    return response.choices[0].message.content or ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", nargs="?", default="你好，请用一句中文介绍你自己。")
    parser.add_argument("--check-tools", action="store_true", help="验证模型的 Tool Calling 能力")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key.lower() in {"your-api-key", "your_api_key", "sk-xxx"}:
        print("缺少 OPENAI_API_KEY：请将真实 API Key 填入项目根目录的 .env 后重试。", file=sys.stderr)
        return 2
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com").strip()
    model = os.getenv("OPENAI_MODEL", "deepseek-flash").strip()
    if not model or urlparse(base_url).scheme not in {"https", "http"} or not urlparse(base_url).hostname:
        print("请检查 .env 中的 OPENAI_MODEL 和 OPENAI_BASE_URL。", file=sys.stderr)
        return 2
    # DeepSeek defaults to thinking mode; disable it for this small connectivity demo.
    options = {}
    if urlparse(base_url).hostname == "api.deepseek.com":
        options["extra_body"] = {"thinking": {"type": "disabled"}}
    try:
        with OpenAI(api_key=api_key, base_url=base_url, timeout=60.0, max_retries=1) as client:
            if args.check_tools:
                reply = check_tools(client, model, options)
            else:
                response = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": args.message}], **options
                )
                reply = response.choices[0].message.content or ""
        if not reply.strip():
            print("模型未返回文本内容，请检查模型配置。", file=sys.stderr)
            return 1
        print(reply)
        return 0
    except APITimeoutError:
        print("模型请求超时，请检查网络或稍后重试。", file=sys.stderr)
    except APIConnectionError:
        print("无法连接模型 API，请检查地址、网络和代理设置。", file=sys.stderr)
    except APIStatusError as exc:
        print(f"模型 API 返回 HTTP {exc.status_code}；请检查 Key、余额、模型名和服务状态。", file=sys.stderr)
    except (ValueError, IndexError):
        print("模型响应或工具参数不符合预期，请检查服务是否兼容 Chat Completions 和 Tool Calling。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
