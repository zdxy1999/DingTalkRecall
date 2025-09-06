#!/usr/bin/env python

import argparse
import logging
import ssl
import os
import uuid
import pytz

import certifi  # 添加这一行
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dingtalk_stream import AckMessage
import dingtalk_stream

from static.handler.message_handler import call_dify, daily_reminder_dify
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 添加以下代码来设置证书路径
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()


def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def setup_scheduler():
    """设置定时任务"""
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Shanghai'))

    # 添加每日提醒任务，每天上午9点执行
    # 您可以根据需要修改时间，例如：
    # CronTrigger(hour=9, minute=0) 表示每天9:00执行
    # CronTrigger(hour=18, minute=30) 表示每天18:30执行
    scheduler.add_job(
        func=daily_reminder_dify,
        trigger=CronTrigger(hour=9, minute=0),
        id='daily_reminder',
        name='Daily Reminder Task',
        replace_existing=True
    )
    scheduler.start()
    return scheduler

class CalcBotHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self, logger: logging.Logger = None):
        super(dingtalk_stream.ChatbotHandler, self).__init__()
        if logger:
            self.logger = logger

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        self.logger.info('receive callback: %s' % callback)
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        self.reply_text("答案正在生成中...", incoming_message)
        try:
            result = await call_dify(incoming_message.text.content)
        except Exception as e:
            result = 'Error: %s' % e
            self.reply_text("！！！答案生成异常" + result, incoming_message)
            return AckMessage.STATUS_SYSTEM_EXCEPTION, 'OK'

        response = result
        # self.reply_markdown_card(at_sender=True, title="计算结果", markdown=response, incoming_message=incoming_message)
        md_title = "title"+str(uuid.uuid4()).replace('-', '')[:10]

        self.reply_text("以下是对问题的答案", incoming_message)
        self.reply_markdown(title=md_title, text=response, incoming_message=incoming_message)
        return AckMessage.STATUS_OK, 'OK'


def main():
    load_dotenv()
    logger = setup_logger()
    setup_scheduler()
    #options = define_options()

    credential = dingtalk_stream.Credential(os.getenv('DINGTALK_CLIENT_ID'), os.getenv('DINGTALK_CLIENT_SECRET'))
    client = dingtalk_stream.DingTalkStreamClient(credential)

    # 添加SSL上下文配置以使用certifi证书
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(certifi.where())
    client.ssl_context = ssl_context

    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, CalcBotHandler(logger))
    client.start_forever()


if __name__ == '__main__':
    main()