# -*- coding: utf-8 -*-#

# Author:Zephyrchole
# @software: PyCharm
# @file: PerfectedWechatPCAPI.py
# @time: 2020/11/3 17:08 
from WechatPCAPI import WechatPCAPI
import logging
from queue import Queue
from time import sleep


class Friend:
    def __init__(self, wxid, wechat_number, nickname, remarkname):
        self.wxid = wxid
        self.wechat_number = wechat_number
        self.nickname = nickname
        self.remarkname = remarkname


class Member:
    def __init__(self, wxid, wechat_number, name):
        self.wxid = wxid
        self.wechat_number = wechat_number
        self.name = name


class Chatroom:
    members = []

    def __init__(self, wxid, name):
        self.wxid = wxid
        self.name = name


class PerfectedWechatPCAPI(WechatPCAPI):
    logging.basicConfig(level=logging.INFO)
    message_queue = Queue()
    friends = []
    chatrooms = []

    def __init__(self):
        super(PerfectedWechatPCAPI, self).__init__(on_message=self.on_message, log=logging)
        super().start_wechat(block=False)
        while not super().get_myself():
            sleep(5)
        print("登陆成功")
        self.update_info()

    def update_info(self):
        self.friends = []
        self.chatrooms = []
        self.collect_info()

    def collect_info(self):
        self.get_friends_and_chatrooms()
        sleep(1)
        self.get_chatroom_members()

    def get_friends_and_chatrooms(self):
        super().update_frinds()

    def get_chatroom_members(self):
        for chatroom in self.chatrooms:
            super().get_member_of_chatroom(chatroom.wxid)

    def on_message(self, message):
        logging.debug(message)
        self.info_manager(message)

    def info_manager(self, message):
        msg_type = message.get("type")
        msgType_fun = {"member::chatroom": self.info_chatroom_member, "friend::person": self.info_friend,
                       "friend::chatroom": self.info_chatroom}
        msgType_fun.get(msg_type, self.message_queue.put)(message)

    def info_chatroom_member(self, message):
        data = message.get("data")
        chatroom_wxid = data.get("chatroom_id")
        member_wxid = data.get("wx_id")
        member_name = data.get("wx_nickname").encode("gbk", "replace").decode("gbk", "replace")
        member_wechat_number = data.get("wx_id_search")
        new_member = Member(member_wxid, member_wechat_number,member_name)
        for chatroom in self.chatrooms:
            if chatroom.wxid == chatroom_wxid:
                chatroom.members.append(new_member)
                break

    def info_friend(self, message):
        data = message.get("data")
        friend_nickname = data.get("wx_nickname").encode("gbk", "replace").decode("gbk", "replace")
        friend_wxid = data.get("wx_id")
        friend_wechat_number = data.get("wx_id_search")
        new_friend = Friend(friend_wxid, friend_wechat_number, friend_nickname, '')
        self.friends.append(new_friend)

    def info_chatroom(self, message):
        data = message.get("data")
        chatroom_name = data.get("chatroom_name").encode("gbk", "replace").decode("gbk", "replace")
        chatroom_wxid = data.get("chatroom_id")
        new_chatroom = Chatroom(chatroom_wxid, chatroom_name)
        self.chatrooms.append(new_chatroom)


def main():
    wx_inst = PerfectedWechatPCAPI()
    while True:
        message = wx_inst.message_queue.get()
        print(message)


if __name__ == '__main__':
    main()
