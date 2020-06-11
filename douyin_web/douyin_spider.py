# -*- coding: utf-8 -*-
# @Author: Mr.Yang
# @Date: 2020/5/8 pm 2:37


import requests
import json
import time
from loguru import logger
import re
import traceback

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

def deal_time(release_time):
    if len(str(release_time)) > 10:
        release_time = str(release_time)[0:10]
    release_time = int(release_time)
    # 转换成localtime
    release_time = time.localtime(release_time)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    release_time = time.strftime("%Y-%m-%d %H:%M:%S", release_time)
    return release_time

headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-CN,zh;q=0.9"
}

proxies = {}
def get_sign(uid):
    uid = '108772418543'
    response = requests.get('https://www.iesdouyin.com/share/user/{}'.format(uid),headers=headers,verify=False)
    # tac_ = re.findall('<script>tac=\'(.*?)\'</script>',response.text)[0]
    # tac = tac_.encode('utf-8').decode("unicode-escape")
    # print(tac)
    tac = re.search(r"tac='([\s\S]*?)'</script>",response.text).group(1)
    tac = tac.split("|")[0]
    data = {
        "tac_": tac,
        'u_id': uid
    }
    response = requests.post('http://192.168.2.214:3000/get_sign', data=data)
    sign = response.json().get("msg")
    return sign

@debug
def build_request(uid,max_cursor=0):
    sign = get_sign(uid)
    # url = "https://www.iesdouyin.com/web/api/v2/aweme/post/?user_id={}&sec_uid=&count=21&max_cursor={}&aid=1128&_signature={}"
    url = "https://www.iesdouyin.com/web/api/v2/aweme/post/?&sec_uid={}&count=21&max_cursor={}&aid=1128&_signature={}"
    url = url.format(uid.strip(), max_cursor, sign)
    response = requests.get(url, headers=headers, verify=False, proxies=proxies)
    datas = response.json()
    return datas

@debug
def get_next_max_cursor(uid, datas, limit_time, task_json,callbackUrl):
    if datas.get("has_more"):
        next_page = datas.get("max_cursor")
        datas = build_request(uid, max_cursor=next_page)
        parse_json_data(uid, datas, limit_time, task_json, callbackUrl)
    else:
        return []

@debug
def parse_json_data(uid, datas, limit_publish_time, task_json, callbackUrl):

    data_list = datas.get("aweme_list")
    save_list = []

    limit_time = ""
    for data in data_list:
        save_dict = {}
        assetCode = data.get("statistics").get("aweme_id", "")
        title = data.get("desc", "")
        description = data.get("desc", "")
        try:
            createDate = re.findall('(1\d{9})\.',str(data), re.S | re.M)[0]
        except:
            continue
        picUrl = data.get("video").get("cover").get("url_list")[0]
        videoUrl = data.get("video").get("download_addr").get("url_list")[-1]
        visitCount = data.get("statistics").get("play_count", 0)
        rebackCount = data.get("statistics").get("comment_count", 0)
        shareCount = data.get("statistics").get("share_count", 0)
        repostsCount = data.get("statistics").get("forward_count", 0)
        likeCount = data.get("statistics").get("digg_count", 0)
        downloadCount = data.get("statistics").get("download_count", 0)


        #用户信息
        accountName = data.get("author").get("unique_id", "")
        imgUri = data.get("author").get("avatar_thumb").get("url_list", [])[0]
        sourceName = data.get("author").get("nickname", "")
        secUid = data.get("author").get("sec_uid", "")


        # logger.info(assetCode)
        # logger.info(title)
        # logger.info(description)
        # logger.info(deal_time(createDate))
        # logger.info(picUrl)
        # logger.info(videoUrl)
        # logger.info(visitCount)
        # logger.info(rebackCount)
        # logger.info(shareCount)
        # logger.info(repostsCount)
        # logger.info(likeCount)
        # logger.info(downloadCount)
        # logger.info(accountName)
        # logger.info(imgUri)
        # logger.info(sourceName)
        # logger.info(secUid)


        save_dict["assetCode"] = assetCode
        save_dict["title"] = title
        save_dict["description"] = description
        save_dict["createDate"] = str(createDate) + "000"
        save_dict["picUrl"] = picUrl
        save_dict["visitCount"] = visitCount
        save_dict["rebackCount"] = rebackCount
        save_dict["videoUrl"] = videoUrl
        save_dict["shareCount"] = shareCount
        save_dict["repostsCount"] = repostsCount
        save_dict["likeCount"] = likeCount
        save_dict["repostsCount"] = repostsCount
        save_dict["downloadCount"] = downloadCount
        save_dict["accountName"] = accountName
        save_dict["imgUri"] = imgUri
        save_dict["sourceName"] = sourceName
        save_dict["secUid"] = secUid

        if deal_time(createDate) < deal_time(limit_publish_time):
            limit_time = ""
            break
        else:
            save_list.append(save_dict)
            limit_time = limit_publish_time


    return_datas = {
        "data": {
            "obj": None,
            "list": save_list
            }
        }
    return_datas['task'] = task_json

    #将数据传输到服务器
    if return_datas.get("data").get("list"):

        result = send_data(callbackUrl, return_datas)
        logger.debug(return_datas)
        logger.info(result)

    #下一页更新
    if limit_time:
        get_next_max_cursor(uid, datas, limit_time, task_json, callbackUrl)


@debug
def send_data(callbackUrl,datas):
    response = requests.post(callbackUrl, data={"value": json.dumps(datas)})
    return response.text

@debug
def main(task_json):

    user_id = task_json['gatherUserId']
    limit_publish_time = task_json['limit_publish_time']

    callbackUrl = task_json["callbackUrl"]
    datas = build_request(user_id, max_cursor=0)
    parse_json_data(user_id, datas, limit_publish_time, task_json, callbackUrl)


# if __name__ == '__main__':
#     # mq中的任务
#     # TASK = {"accountId": "70", "callbackUrl": "http://localhost:8081/MiaVideoList!getMiaVideoJsonList.action",
#     #         "gatherUserId": "MS4wLjABAAAApzxDEGe9TRPzxm5MkCTatNViFCBMGvStxISqLwHAtjc",
#     #         "hashCode": -684732892423992557, "limit_publish_time": 1588117285000, "nextCursor": "", "pageNo": 1,
#     #         "taskType": "account_assets", "websiteName": "\u4e2d\u56fd\u65e5\u62a5\u7f51", "websiteType": 1}
#
#     import douyin_web.mq_tools as pq_mq
#
#     mq = pq_mq.MqClient((pq_mq.MqConfig(ip="", user="",
#                                         password="", virtual='/')))
#
#     QUEUE_TASK = "video_task_dy"
#     while True:
#         try:
#             task = mq.get_message(QUEUE_TASK)
#
#             if task:
#                 logger.debug(f"获取[mq] 任务{task}")
#                 main(json.loads(task))
#                 time.sleep(3)
#             else:
#                 logger.debug("[mq] 暂时无数据任务，睡眠30*2*2秒，再次扫描")
#                 time.sleep(30*2*2)
#                 continue
#         except Exception as err:
#             # logger.debug("[mq] 暂时无数据任务，睡眠30秒，再次扫描")
#             # time.sleep(30)
#             # continue
#             raise err
#

