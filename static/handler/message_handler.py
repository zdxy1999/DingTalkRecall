import asyncio
import os

import aiohttp
from dotenv import load_dotenv


async def call_dify(user_input: str="", user: str="default-user", token: str=os.getenv("DIFY_API_KEY"), url: str=os.getenv("DIFY_URL")):
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
        "response_mode": "blocking",
        "user": user
    }

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                return 'dify 调用异常' + str(response.status)

            response_text = await response.text()
            print("响应内容:", response_text)

            # 如果返回是 JSON，可以直接解析

            json_response = await response.json()
            print("JSON 响应:", json_response)
            content = json_response.get("data", {}).get("outputs", "").get("text", "")
            return content
        return 'dify 调用异常'

async def daily_reminder_dify():
    await call_dify(user_input="每日提醒", token=os.getenv("DAILY_REMINDER_API_KEY"), url=os.getenv("DIFY_URL"))


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(daily_reminder_dify())
    # daily_reminder_dify()