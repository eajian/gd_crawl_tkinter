import tkinter
from tkinter import messagebox
import requests
import time
import math
import threading
import inspect
import ctypes

import os
import xlsxwriter
import re

from utils.city import get_city

headers = {
    'Host':'restapi.amap.com',
    'Connection':'keep-alive',
    'Cache-Control':'max-age=0',
    'Accept': 'text/html, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
    'DNT':'1',
    'Referer': 'http://www.super-ping.com/?ping=www.google.com&locale=sc',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
}


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class Start(object):
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.iconbitmap('assets/ico/ico.ico')
        self.root.title('版本 0.0.3')
        # 窗体居中 - S
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = 800
        wh = 380
        x = (sw - ww) / 2
        y = (sh - wh) / 2
        self.root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
        self.root.resizable(False, False) # 窗体禁止拉伸
        # 窗体居中 - E
        self.keys_label = tkinter.Label(self.root, text='密钥: ')
        self.input_keys = tkinter.Entry(self.root, show='*', width=30)
        self.key_word_label = tkinter.Label(self.root, text='关键词: ')
        self.input_key_word = tkinter.Entry(self.root, width=30)
        self.time_label = tkinter.Label(self.root, text='延迟: ')
        self.input_time = tkinter.Entry(self.root, width=5)
        self.todo_btn = tkinter.Button(self.root, command=self.todo_crawl, text="开始采集", width=10)
        #
        self.box = tkinter.Frame(self.root)
        self.box.place(x=10, y=80)
        self.console_s = tkinter.Scrollbar(self.box)
        self.console_s.pack(side='right', fill='y')
        self.console = tkinter.Listbox(self.box, width=109, height=16, bg='#000', fg='#00FF00', yscrollcommand=self.console_s.set)
        self.console.pack(side='right', fill='both')
        self.console_s.config(command=self.console.yview)
        self.keys = ''
        self.key_word = ''
        self.location = ''
        self.sf = ''
        self.sheet = '初始化'
        self.time = 5
        self.thread1 = threading.Thread(target=self.init_get) # 做为变量
        # v3
        self.m_box = tkinter.Frame(self.root, width=200, height=22, )
        self.check_label = tkinter.Label(self.m_box, text='数据类型: ')
        self.check_v1 = tkinter.IntVar()
        self.check_v2 = tkinter.IntVar()
        self.check_v1.set(1) # 设置个默认值
        self.check_btn1 = tkinter.Checkbutton(self.m_box, text='手机', variable=self.check_v1)
        self.check_btn2 = tkinter.Checkbutton(self.m_box, text='固话', variable=self.check_v2)
        self.check1 = 1
        self.check2 = 1
        # v3



    def stop_crawl(self):
        _async_raise(self.thread1.ident, SystemExit)
        # 转换按钮
        self.todo_btn['text'] = '开始采集'
        self.todo_btn['command'] = self.todo_crawl
        self.console.insert('end', '\n采集结束')
        self.console.yview_moveto(1)  # 更新滚动到底部

    def gui_show(self):
        self.keys_label.place(x=10, y=10)
        self.input_keys.place(x=60, y=10)
        self.key_word_label.place(x=10, y=45)
        self.input_key_word.place(x=60, y=45)
        #
        self.time_label.place(x=280, y=10)
        self.input_time.place(x=320, y=10)
        #
        self.todo_btn.place(x=280, y=40)
        #
        self.input_time.insert(0, self.time)
        self.input_key_word.insert(0, '请输入关键词...')
        # v3
        self.m_box.place(x=380, y=10)
        self.check_label.pack(side='left')
        self.check_btn1.pack(side='left')
        self.check_btn2.pack(side='left')
        # v3


    def todo_crawl(self):
        self.keys = self.input_keys.get()
        self.key_word = self.input_key_word.get()
        self.time = int(self.input_time.get())
        self.check1 = self.check_v1.get()
        self.check2 = self.check_v2.get()
        if self.check1 == 0 and self.check2 == 0:
            return tkinter.messagebox.showinfo(title='信息', message='请最少选择个输出数据类型')
        if not self.keys:
            return tkinter.messagebox.showinfo(title='信息', message='请填写正确的密钥')
        if not self.key_word:
            return tkinter.messagebox.showinfo(title='信息', message='请填写关键词')
        if not self.time:
            return tkinter.messagebox.showinfo(title='信息', message='请填写延迟时间')
        # 转换按钮
        self.todo_btn['text'] = '停止'
        self.todo_btn['command'] = self.stop_crawl
        self.console.insert('end', '正在采集...')
        self.console.yview_moveto(1)  # 更新滚动到底部
        # 开启多线程 - 修改变量
        self.thread1 = threading.Thread(target=self.init_get)
        self.thread1.start()

    def init_get(self):
        for i in get_city():
            self.sf = i['name']
            self.console.insert('end', '正在采集[' + i['name'] + '] 共' + str(len(i['next'])) + '个城市')
            self.console.yview_moveto(1)  # 更新滚动到底部
            for x in i['next']:
                self.console.insert('end', '   采集 >' + x['name'] + '< 坐标 ' + x['center'])
                self.console.yview_moveto(1)  # 更新滚动到底部
                self.location = x['center']
                # v2 加上判断是否有这个文件 有就跳过
                if not os.path.exists('data/'+self.key_word + '/' + self.sf + '/' + x['name'] + '_data.xlsx'):
                # v2
                    self.get_info_init(self.keys, self.key_word, self.location, x['name'])
                    time.sleep(self.time)
                else:
                    self.console.insert('end', '   数据已经存在,跳过~ ')
                    self.console.yview_moveto(1)  # 更新滚动到底部
            # test
            # self.location = i['next'][0]['center']
            # self.get_info_init(self.keys, self.key_word, self.location, i['next'][0]['name'])
            # time.sleep(self.time)

    def get_info_init(self, keys, key_word, location, city):
        time.sleep(self.time)
        page = 1
        urls = 'http://restapi.amap.com/v3/place/around?key=' + keys + '&location=' + location + '&keywords=' + key_word + '&offset=25&page=' + str(page) + '&radius=50000'
        res_list = []
        res = requests.get(urls, headers).json()
        # 先判断一次回调
        if res['status'] == '1':
            pages = math.ceil(int(res['count']) / 25)
            self.console.insert('end', '      需采集共 ' + str(pages) + ' 页 ')
            self.console.insert('end', '      第 1 页 ')
            self.console.yview_moveto(1)  # 更新滚动到底部
            for e in res['pois']:
                if e['tel']:
                    phone = []
                    call = []
                    telephone = e['tel'].split(';')
                    # 全选
                    if self.check1 == 1 and self.check2 == 1:
                        for p, pval in enumerate(telephone):
                            ret = re.match(r"^1[23456789]\d{9}$", pval)
                            if ret:
                                phone.append(pval)
                            else:
                                call.append(pval)
                        #
                        if len(phone) != 0 or len(call) != 0:
                            e_address = e['address'] if e['address'] else '空'
                            e_name = e['name'] if e['name'] else '空'
                            res_list.append({'名字': e_name, '手机': (";".join(phone)), '固话': (";".join(call)), '地址': e_address})
                            self.console.insert('end', '      名字:' + e_name + ' / 手机:' + (";".join(phone)) + ' / 固话:' + (";".join(call)) + '/ 地址:' + e_address)
                            self.console.yview_moveto(1)  # 更新滚动到底部
                    # 全选
                    # 只选手机
                    elif self.check1 == 1:
                        for p, pval in enumerate(telephone):
                            ret = re.match(r"^1[23456789]\d{9}$", pval)
                            if ret:
                                phone.append(pval)
                        if len(phone) != 0:
                            e_address = e['address'] if e['address'] else '空'
                            e_name = e['name'] if e['name'] else '空'
                            res_list.append({'名字': e_name, '手机': (";".join(phone)), '固话': (";".join(call)), '地址': e_address})
                            self.console.insert('end', '      名字:' + e_name + ' / 手机:' + (";".join(phone)) + ' / 固话:' + (";".join(call)) + '/ 地址:' + e_address)
                            self.console.yview_moveto(1)  # 更新滚动到底部
                    # 只选手机
                    # 只选固话
                    elif self.check2 == 1:
                        for p, pval in enumerate(telephone):
                            ret = re.match(r"^1[23456789]\d{9}$", pval)
                            if not ret:
                                call.append(pval)
                        if len(call) != 0:
                            e_address = e['address'] if e['address'] else '空'
                            e_name = e['name'] if e['name'] else '空'
                            res_list.append({'名字': e_name, '手机': (";".join(phone)), '固话': (";".join(call)), '地址': e_address})
                            self.console.insert('end', '      名字:' + e_name + ' / 手机:' + (";".join(phone)) + ' / 固话:' + (";".join(call)) + '/ 地址:' + e_address)
                            self.console.yview_moveto(1)  # 更新滚动到底部
                    # 只选固话

            # 分页采集
            for other in range(pages - 1):
                time.sleep(self.time)
                new_page = other + 2
                self.console.insert('end', '      第 ' + str(new_page) + ' 页 ')
                self.console.yview_moveto(1)  # 更新滚动到底部
                new_urls = 'http://restapi.amap.com/v3/place/around?key=' + keys + '&location=' + location + '&keywords=' + key_word + '&offset=25&page=' + str(new_page) + '&radius=50000'
                new_res = requests.get(new_urls, headers).json()
                for new_e in new_res['pois']:
                    if new_e['tel']:
                        phone = []
                        call = []
                        telephone = new_e['tel'].split(';')
                        # 全选
                        if self.check1 == 1 and self.check2 == 1:
                            for p, pval in enumerate(telephone):
                                ret = re.match(r"^1[23456789]\d{9}$", pval)
                                if ret:
                                    phone.append(pval)
                                else:
                                    call.append(pval)
                            #
                            if len(phone) != 0 or len(call) != 0:
                                new_address = new_e['address'] if new_e['address'] else '空'
                                new_name = new_e['name'] if new_e['name'] else '空'
                                res_list.append({'名字': new_name, '手机': (";".join(phone)), '固话': (";".join(call)), '地址': new_address})
                                self.console.insert('end', '      名字:' + new_name + ' / 手机:' + (";".join(phone)) + '/ 固话:' + (";".join(call)) + '/ 地址:' + new_address)
                                self.console.yview_moveto(1)  # 更新滚动到底部
                        # 全选
                        # 只选手机
                        elif self.check1 == 1:
                            for p, pval in enumerate(telephone):
                                ret = re.match(r"^1[23456789]\d{9}$", pval)
                                if ret:
                                    phone.append(pval)
                            if len(phone) != 0:
                                new_address = new_e['address'] if new_e['address'] else '空'
                                new_name = new_e['name'] if new_e['name'] else '空'
                                res_list.append({'名字': new_name, '手机': (";".join(phone)), '固话': (";".join(call)), '地址': new_address})
                                self.console.insert('end', '      名字:' + new_name + ' / 手机:' + (";".join(phone)) + '/ 固话:' + (";".join(call)) + '/ 地址:' + new_address)
                                self.console.yview_moveto(1)  # 更新滚动到底部
                        # 只选手机
                        # 只选固话
                        elif self.check2 == 1:
                            for p, pval in enumerate(telephone):
                                ret = re.match(r"^1[23456789]\d{9}$", pval)
                                if not ret:
                                    call.append(pval)
                            if len(call) != 0:
                                new_address = new_e['address'] if new_e['address'] else '空'
                                new_name = new_e['name'] if new_e['name'] else '空'
                                res_list.append({'名字': new_name, '手机': (";".join(phone)), '固话': (";".join(call)), '地址': new_address})
                                self.console.insert('end', '      名字:' + new_name + ' / 手机:' + (";".join(phone)) + '/ 固话:' + (";".join(call)) + '/ 地址:' + new_address)
                                self.console.yview_moveto(1)  # 更新滚动到底部
                        # 只选固话
            self.write_info(res_list, city)
        else:
            tkinter.messagebox.showerror(title='信息', message='采集失败，密钥或参数错误！')
            self.root.destroy()

    def write_info(self, res_list, city): # 写入
        if res_list:
            if not os.path.exists('data/'+self.key_word):
                os.mkdir('data/'+self.key_word)
            if not os.path.exists('data/'+self.key_word+'/' + self.sf):
                os.mkdir('data/'+self.key_word+'/' + self.sf)

            workbook = xlsxwriter.Workbook('data/'+self.key_word+'/' + self.sf + '/' + city + '_data.xlsx')
            worksheet = workbook.add_worksheet(city)
            for index, val in enumerate(res_list):
                worksheet.write(index, 0, val['名字'])
                worksheet.write(index, 1, val['手机'])
                worksheet.write(index, 2, val['固话'])
                worksheet.write(index, 3, val['地址'])
            workbook.close()


def main():
    L = Start()
    L.gui_show()
    tkinter.mainloop()


# 程序入口
if __name__ == '__main__':
    main()
