manage command
manage.py collectstatic 收集静态文件
manage.py runserver_plus --cert server.crt

uwsgi
uwsgi --ini uwsgin.ini  启动
uwsgi --reload uwsgi/uwsgi.pid  重载
uwsgi --stop uwsgi/uwsgi.pid  停止
uwsgi --connect-and-read uwsgi/uwsgi.status  查看状态


nginx
sudo /etc/init.d/nginx start
sudo /etc/init.d/nginx stop
