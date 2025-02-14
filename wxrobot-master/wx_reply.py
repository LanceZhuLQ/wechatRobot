# 好友功能
import re
import tuling_robot
import json
import pytz
from datetime import datetime, time, timedelta
import hashlib


def getHash(f):
    line=f.readline()
    hash=hashlib.md5()
    while(line):
        hash.update(line)
        line=f.readline()
    return hash.hexdigest()
def IsHashEqual(f1,f2):
    str1=getHash(f1)
    str2=getHash(f2)
    return str1==str2


def getYesterday():
	today=datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d')
	oneday=datetime.timedelta(days=1)
	yesterday=today-oneday
	return yesterday

def auto_accept_friends(msg):
    """自动接受好友"""
    # 接受好友请求
    new_friend = msg.card.accept()
    # 向新的好友发送消息
    new_friend.send('我已自动接受了你的好友请求')


def auto_reply(msg):
    """自动回复"""
    # 关键字回复 or 图灵机器人回复
    # handle_withdraw_msg(msg)
    keyword_reply(msg)

    # 图灵机器人链接好了再开启
    # keyword_reply(msg) or tuling_reply(msg)


def keyword_reply(msg):
    if '功能介绍' in msg.text:
        response = "1.疫情签到\n2.今日情况比对\n3.未完待续。。。"
        return msg.reply(response)
    if '疫情签到' in msg.text:
        msgList = msg.text.split('-')
        if len(msgList) != 4:
            return msg.reply('请参照格式 疫情签到-朱岚清-爱尔兰科克-身体健康')
        name = msgList[1]
        location = msgList[2]
        healthy = msgList[3]
        tz = pytz.timezone("Asia/Shanghai")
        today = datetime.now(tz).date()
        fileName = "data/"+str(today)
        Signed = False
        count = int(0)
        for line in open(fileName):
            count = count+1
            lineList = line.split('-')
            if (lineList[0] == name):
                Signed = True
        if Signed == True:
            response = "请勿重复签到，如需修改地点，或健康情况，请联系管理员"
        if Signed == False:
            response = "恭喜签到成功！\n"+"姓名:"+name+"\n地点:"+location+"\n健康情况:"+healthy
            dict = {}

            dict['name'] = name
            dict['location'] = location
            dict['healthy'] = healthy

            f = open(fileName,'a')
            recordInfo = name+"-"+location+"-"+healthy+"\n"
            f.write(recordInfo)
            f.close()

        if count == 4:
            response = response + "\n\n" + "今日签到结束"
            return msg.reply(response)
        return msg.reply(response)
    if '今日情况比对' in msg.text:
        tz = pytz.timezone("Asia/Shanghai")
        today = datetime.now(tz).date()
        # yesterday = datetime.now(tz).date() - timedelta(days=1)
        # yesterdayFileName = "data/"+str(yesterday)
        todayFileName = "data/"+str(today)
        demoFileName = "data/demo"
        responseOfNoSignup = ""
        responseOfChangingLocation = ""
        responseOfChangingHealthy = ""
        for line in open(demoFileName):
            Signup = False
            ChangingOfLocation = False
            ChangingOfHealthy = False
            for line02 in open(todayFileName):
                lineList = line.split('-')
                line02List = line02.split('-')
                if (lineList[0] == line02List[0]):
                    Signup = True
                    if (lineList[1] != line02List[1]):
                        ChangingOfLocation = True
                    if (lineList[2] != line02List[2]):
                        ChangingOfHealthy = True


            if Signup == False:
                responseOfNoSignup = responseOfNoSignup + lineList[0] + " "
            elif Signup == True:
                if ChangingOfLocation == True:

                    responseOfChangingLocation = responseOfChangingLocation + lineList[0]+ " "
                if ChangingOfHealthy == True:
                    responseOfChangingHealthy = responseOfChangingHealthy + lineList[0]+ " "

        response = "今日未签到同学名字：\n"+responseOfNoSignup+"\n\n"+"今日地址变更同学名字：\n"+responseOfChangingLocation+"\n\n"+"今日健康情况变更同学名字：\n"+responseOfChangingHealthy+"\n"

        return msg.reply("比对结果：\n" + response)

    """关键字回复"""
    if '在吗' in msg.text:
        return msg.reply('请直奔主题， 看到后会尽快回复（机器人自动回复）')
    if '机器人测试' in msg.text:
        return msg.reply('我在正常工作呀！（机器人自动回复）')
    else:
        return msg.reply('其他（机器人自动回复）')
    pass


def tuling_reply(msg):
    """图灵机器人回复"""
    tuling_robot.auto_reply(msg)


def handle_system_msg(msg):
    """处理系统消息"""
    raw = msg.raw
    # 4表示消息状态为撤回
    if raw['Status'] == 4 and msg.bot.is_forward_revoke_msg:
        # 转发撤回的消息
        forward_revoke_msg(msg)


def forward_revoke_msg(msg):
    """转发撤回的消息"""
    # 获取被撤回消息的ID
    revoke_msg_id = re.search('<msgid>(.*?)</msgid>', msg.raw['Content']).group(1)
    # bot中有缓存之前的消息，默认200条
    for old_msg_item in msg.bot.messages[::-1]:
        # 查找撤回的那条
        if revoke_msg_id == str(old_msg_item.id):
            # 判断是群消息撤回还是好友消息撤回
            if old_msg_item.member:
                sender_name = '群「{0}」中的「{1}」'.format(old_msg_item.chat.name, old_msg_item.member.name)
            else:
                sender_name = '「{}」'.format(old_msg_item.chat.name)
            # 名片无法转发
            if old_msg_item.type == 'Card':
                sex = '男' if old_msg_item.card.sex == 1 else '女' or '未知'
                msg.bot.master.send('「{0}」撤回了一张名片：\n名称：{1}，性别：{2}'.format(sender_name, old_msg_item.card.name, sex))
            else:
                # 转发被撤回的消息
                old_msg_item.forward(msg.bot.master,
                                     prefix='{}撤回了一条消息：'.format(sender_name, get_msg_chinese_type(old_msg_item.type)))
            return None


def get_msg_chinese_type(msg_type):
    """转中文类型名"""
    if msg_type == 'Text':
        return '文本'
    if msg_type == 'Map':
        return '位置'
    if msg_type == 'Card':
        return '名片'
    if msg_type == 'Note':
        return '提示'
    if msg_type == 'Sharing':
        return '分享'
    if msg_type == 'Picture':
        return '图片'
    if msg_type == 'Recording':
        return '语音'
    if msg_type == 'Attachment':
        return '文件'
    if msg_type == 'Video':
        return '视频'
    if msg_type == 'Friends':
        return '好友请求'
    if msg_type == 'System':
        return '系统'
