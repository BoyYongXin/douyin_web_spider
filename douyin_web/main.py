# -*- coding: utf-8 -*-
# @Author: Mr.Yang
# @Date: 2020/5/8 pm 2:37

import douyin_web.mq_tools as pq_mq
from loguru import logger
from douyin_web import douyin_spider
import time
import json
from douyin_web import douyin_timer
from datetime import datetime


QUEUE_TASK = "video_task_dy"

# # 方式一 : 通过while + sleep 完成每间隔多长时间，扫一轮任务，跑一波数据
# mq = pq_mq.MqClient((pq_mq.MqConfig(ip="", user="",
#                                                  password="", virtual='/')))
# while True:
#     try:
#         task = mq.get_message(QUEUE_TASK)
#
#         if task:
#             logger.debug(f"获取[mq] 任务{task}")
#             douyin_spider.main(json.loads(task))
#             time.sleep(3)
#         else:
#             logger.debug("[mq] 暂时无数据任务，睡眠30*2*2秒，再次扫描")
#             time.sleep(30*2*2)
#             continue
#     except Exception as err:
#         raise err


# 方式二 : 通过threading.timer 完成每间隔多长时间，扫一轮任务，跑一波数据
class Singleton(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)

        return cls._inst

class Begin(Singleton):

    def __init__(self):
        self.mq = pq_mq.MqClient((pq_mq.MqConfig(ip="", user="",
                                                 password="", virtual='/')))
        
    def start_spider(self, name, result):
        try:
            self.mq = pq_mq.MqClient((pq_mq.MqConfig(ip="", user="",
                                                     password="", virtual='/')))
            logger.debug(f"[mq] {name},{result}")
            while True:
                task = self.mq.get_message(QUEUE_TASK)

                if task:
                    logger.debug(f"获取[mq] 任务{task}")
                    douyin_spider.main(json.loads(task))
                    time.sleep(0.5)
                else:
                    logger.debug("[mq] 暂时无数据任务，将在下一个小时，第3分钟再次扫描")
                    break

        except Exception as err:
            raise err

# 测试启动
# start = datetime.now().replace(minute=3, second=0, microsecond=0)
# tmr = douyin_timer.MyTimer(start, 60*60, Begin().start_spider)
# tmr.start()
# tmr.cancel()


# 扫描任务频率为，每小时的第30分钟进行扫描mq任务
begin = Begin()
start = datetime.now().replace(minute=30, second=0, microsecond=0)
tmr = douyin_timer.MyTimer(start, 60*60, begin.start_spider, ["hello兄弟", "程序启动了，稳妥"])
tmr.start()



