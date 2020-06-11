# -*- coding: utf-8 -*-
# @Author: Mr.Yang
# @Date: 2020/5/8 pm 2:37
import time
from threading import Timer
from datetime import datetime
import traceback
from loguru import logger
def deal_time(release_time):
    if len(str(release_time)) > 10:
        release_time = str(release_time)[0:10]
    release_time = int(release_time)
    # 转换成localtime
    release_time = time.localtime(release_time)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    release_time = time.strftime("%Y-%m-%d %H:%M:%S", release_time)
    return release_time
def debug(func):
    """
    抛出异常
    :param func:
    :return:
    """
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception as err:
            logger.error(err)
            traceback.print_exc()
    return wrapper
class MyTimer( object ):

    def __init__(self, start_time, interval, callback_proc, args=None, kwargs=None):

        self.__timer = None
        self.__start_time = start_time
        self.__interval = interval
        self.__callback_pro = callback_proc
        self.__args = args if args is not None else []
        self.__kwargs = kwargs if kwargs is not None else {}

    @debug
    def exec_callback(self, args=None, kwargs=None):
        self.__callback_pro(*self.__args, **self.__kwargs)
        self.__timer = Timer(self.__interval, self.exec_callback)
        self.__timer.start()

    @debug
    def start(self):
        interval = self.__interval - (datetime.now().timestamp() - self.__start_time.timestamp())
        print(f"任务将于{deal_time(int(time.time())+int(interval))}秒后，开始执行")
        self.__timer = Timer(interval, self.exec_callback)
        self.__timer.start()

    @debug
    def cancel(self):
        self.__timer.cancel()
        self.__timer = None

class AA:
    def hello(self, name, age):
        print("[%s]\thello %s: %d\n" % (datetime.now().strftime("%Y%m%d %H:%M:%S"), name, age))


if __name__ == "__main__":
    aa = AA()
    start = datetime.now().replace(minute=3, second=0, microsecond=0)
    tmr = MyTimer(start, 60*60, aa.hello, ["owenliu", 18])
    tmr.start()
    # tmr.cancel()