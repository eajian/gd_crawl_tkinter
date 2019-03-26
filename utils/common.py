# 输出函数
def console_p(self, e):
    self.console.insert('end',e)
    self.console.yview_moveto(1)
    # 更新滚动到底部
