***\*<1>项目文件介绍：\****

1、获取抖音加密参数文件：/data/docker/douyin_web/signature_server

2、抖音项目爬虫文件：/data/docker/douyin_web/work/douyin_web

 

***\*<2>  signature_serve\****r***\*文件说明：\****

 

1、get_signature.js 	该文件为抖音web分享页面的signature加密js破解文件

2、Server.js  		该文件为启动获取js加密的web接口服务

 

***\*<3>  signature_serve\****r***\*使用方法说明：\****

1、在服务器端安装nodejs

2、安装启动服务的包： npm install express  （建议非全局安装即可）

3、服务启动入口文件为serve.js

4、启动命令： node server.js

5、测试js服务接口否开启成功： curl 192.156.43.223:3000

 

***\*<4>  diuyin_web 文件说明：\****

1、dounyin_spider.py  抖音爬虫和数据存储文件

2、douyin_timer.py   时间定时器代码封装

3、mq_tools.py    操作mq基本封装

4、Main.py      抖音爬虫启动程序入口

5、启动命令：python mian.py 

