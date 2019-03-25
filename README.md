### gd_crawl_tkinter
```
# 导出依赖
pip freeze >requirements.txt 
# 安装依赖
pip install -r requirements.txt
# 加速安装 - 例:django
pip install -i https://pypi.douban.com/simple django
```
### 打包exe
```
pyinstaller -F -w -i ico.ico main.py
# -F 独立文件打包
# -w 不现实终端
# -i 制定icon
PS: 如果有资源文件，需要单独放入同级目录下 
```