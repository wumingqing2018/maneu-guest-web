# Maneu 聪少的订单管理系统

manage 基本操作
> 收集静态文件
> > python3 manage.py collectstatic
> 
> 测试项目启动
> > python3 manage.py runserver 0.0.0.0:8000

uwsgi 基本操作
> 启动
> > uwsgi --ini uwsgin.ini
> 
> 重载
> > uwsgi --reload uwsgi/uwsgi.pid
> 
> 停止
> > uwsgi --stop uwsgi/uwsgi.pid
> 
> 查看状态
> > uwsgi --connect-and-read uwsgi/uwsgi.status
 
配置文件
> nginx.conf 放在这个路径
> 
> > /etc/nginx/nginx.conf
> 
> maneu_store.conf 和 maneu_online.conf 放在这个路径并执行以下链接
> 
> > /etc/nginx/sites-enabled/maneu_online.conf
> 
> uwsgi.ini 放在这个路径
> 
> > /root/maneu/uwsgi.ini

python 迁徙模块
> 导出安装模块的文档
> > pip freeze > readme/requirements.txt
> 
> 安装该文档里的模块
> > pip install -r readme/requirements.txt

github 更新
> git pull git@github.com:wumingqing2018/maneu.git master