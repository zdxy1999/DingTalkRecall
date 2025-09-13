import asyncio
import json
import os

import aiohttp
import requests
from dotenv import load_dotenv


async def call_dify(user_input: str = "", user: str = "default-user", token: str = os.getenv("DIFY_API_KEY"),
              url: str = os.getenv("DIFY_URL")):
    load_dotenv()

    if token is None:
        token = os.getenv("DIFY_API_KEY")
    if url is None:
        url = os.getenv("DIFY_URL")

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {
            "input": user_input
        },
        "response_mode": "streaming",
        "user": user
    }

    try:
        # 使用stream=True来获取流式响应
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=300, verify=False)

        if response.status_code != 200:
            return f'dify 调用异常，状态码: {response.status_code}'

        final_output = ""
        buffer = ""

        # 逐块读取流式响应
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk

                # 处理缓冲区中的完整行
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()

                    if not line:
                        continue

                    # 处理SSE格式
                    if line.startswith('data:'):
                        data_str = line[5:].strip()

                        if data_str == '[DONE]':
                            break

                        try:
                            data = json.loads(data_str)
                            # 只关注workflow_finished事件
                            if data.get('event') == 'workflow_finished':
                                final_output = data.get('data', {}).get('outputs', {}).get('text', '')
                                # 继续读取，确保获取到最后一条

                        except json.JSONDecodeError:
                            continue

        if final_output:
            return final_output
        else:
            return '未收到有效数据：未找到workflow_finished事件'

    except requests.exceptions.Timeout:
        return '请求超时，请稍后重试'
    except requests.exceptions.ConnectionError:
        return '网络连接错误'
    except requests.exceptions.RequestException as e:
        return f'网络请求错误: {str(e)}'
    except Exception as e:
        return f'系统错误: {str(e)}'


def daily_reminder_dify():
    asyncio.run(call_dify(user_input="每日提醒", token=os.getenv("DAILY_REMINDER_API_KEY"), url=os.getenv("DIFY_URL")))


if __name__ == '__main__':
    load_dotenv()
    daily_reminder_dify()
    # daily_reminder_dify()
