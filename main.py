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
        self.root.iconbitmap('ico.ico')
        self.root.title('版本 0.0.1')
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
        self.time = 3
        self.thread1 = threading.Thread(target=self.init_get) # 做为变量
        #

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
        self.input_time.insert(0, 3)
        self.input_key_word.insert(0, '请输入关键词...')

    def todo_crawl(self):
        self.keys = self.input_keys.get()
        self.key_word = self.input_key_word.get()
        self.time = int(self.input_time.get())
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
                self.get_info_init(self.keys, self.key_word, self.location, x['name'])
                time.sleep(self.time)
            # test
            # self.location = i['next'][0]['center']
            # self.get_info_init(self.keys, self.key_word, self.location, i['next'][0]['name'])
            # time.sleep(self.time)

    def get_info_init(self, keys, key_word, location, city):
        time.sleep(self.time)
        page = 1
        urls = 'http://restapi.amap.com/v3/place/around?key=' + keys + '&location=' + location + '&keywords=' + key_word + '&offset=25&page=' + str(page) + '&radius=50000'
        re_list = []
        re = requests.get(urls, headers).json()
        # 先判断一次回调
        if re['status'] == '1':
            pages = math.ceil(int(re['count']) / 25)
            self.console.insert('end', '      需采集共 ' + str(pages) + ' 页 ')
            self.console.insert('end', '      第 1 页 ')
            self.console.yview_moveto(1)  # 更新滚动到底部
            for e in re['pois']:
                if e['tel']:
                    e_address = e['address'] if e['address'] else '空'
                    e_name = e['name'] if e['name'] else '空'
                    re_list.append({'名字': e_name, '电话': e['tel'], '地址': e_address})
                    self.console.insert('end', '      名字:' + e_name + ' / 电话:' + e['tel'] + '/ 地址:' + e_address)
                    self.console.yview_moveto(1)  # 更新滚动到底部
            # 分页采集
            for other in range(pages - 1):
                time.sleep(self.time)
                new_page = other + 2
                self.console.insert('end', '      第 ' + str(new_page) + ' 页 ')
                self.console.yview_moveto(1)  # 更新滚动到底部
                new_urls = 'http://restapi.amap.com/v3/place/around?key=' + keys + '&location=' + location + '&keywords=' + key_word + '&offset=25&page=' + str(
                    new_page) + '&radius=50000'
                new_re = requests.get(new_urls, headers).json()
                for new_e in new_re['pois']:
                    if new_e['tel']:
                        new_address = new_e['address'] if new_e['address'] else '空'
                        new_name = new_e['name'] if new_e['name'] else '空'
                        re_list.append({'名字': new_name, '电话': new_e['tel'], '地址': new_address})
                        self.console.insert('end',
                                            '      名字:' + new_name + '/ 电话:' + new_e['tel'] + '/ 地址:' + new_address)
                        self.console.yview_moveto(1)  # 更新滚动到底部
            self.write_info(re_list, city)
        else:
            tkinter.messagebox.showerror(title='信息', message='采集失败，密钥或参数错误！')
            self.root.destroy()

    def write_info(self, re_list, city): # 写入
        if re_list:
            if not os.path.exists(self.key_word):
                os.mkdir(self.key_word)
            if not os.path.exists(self.key_word+'/' + self.sf):
                os.mkdir(self.key_word+'/' + self.sf)

            workbook = xlsxwriter.Workbook(self.key_word+'/' + self.sf + '/' + city + '_data.xlsx')
            worksheet = workbook.add_worksheet(city)
            for index, val in enumerate(re_list):
                worksheet.write(index, 0, val['名字'])
                worksheet.write(index, 1, val['电话'])
                worksheet.write(index, 2, val['地址'])
            workbook.close()


def main():
    L = Start()
    L.gui_show()
    tkinter.mainloop()


# 程序入口
if __name__ == '__main__':
    main()
