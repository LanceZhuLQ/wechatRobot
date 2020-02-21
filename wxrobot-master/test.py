from datetime import datetime, time, timedelta
import pytz

msg = "疫情签到-朱岚清-爱尔兰科克-身体健康"
msgList = msg.split('-')
# if len(msgList) != 4:
#     return msg.reply('请参照格式 疫情签到-朱岚清-爱尔兰科克-身体健康')
name = msgList[1]
location = msgList[2]
healthy = msgList[3]
response = "恭喜签到成功！\n"+"姓名:"+name+"\n地点:"+location+"\n健康情况:"+healthy
dict = {}

dict['name'] = name
dict['location'] = location
dict['healthy'] = healthy
tz = pytz.timezone("Asia/Shanghai")
today = datetime.now(tz).date()
fileName = "data/"+str(today)
f = open(fileName,'a')
recordInfo = name+"-"+location+"-"+healthy+"\n"
f.write(recordInfo)
f.close()
