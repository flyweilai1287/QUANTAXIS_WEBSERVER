
#执行命令
python setup.py bdist_wheel

#启动
source activate
nohup quantaxis_webserver & >quantaxis_webserver.log
