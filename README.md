### 爬虫 gd_crawl_tkinter
```
# 导出依赖
pip freeze > requirements.txt 
# 安装依赖
pip install -r requirements.txt
# 加速安装 - 例:django
pip install -i https://pypi.douban.com/simple django
```
### 打包exe
```
pyinstaller -F -w -i assets/ico/ico.ico main.py
# -F 独立文件打包
# -w 不显示终端
# -i 制定icon + 路径.ico
PS: 如果有资源文件，需要单独放入同级目录下 
```
```
# V 0.0.4
# 需求：使用代理爬取
1.先采集西刺免费代理 - 国内高匿代理  https://www.xicidaili.com/nn/
2.每天更新下 自建 api

```