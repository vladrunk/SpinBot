#!/bin/zsh

sudo apt update
sudo apt install nginx -y

SCRIPT_PATH=$(dirname "$(realpath "$0")")
echo "Worked dir: $SCRIPT_PATH"

ENV_PATH=$SCRIPT_PATH/env
echo "Activate env: $ENV_PATH"
. $ENV_PATH/bin/activate 

echo "Worked python: $(which python)"
echo "Environment Python version: $(python -V)"
PYTHON=$ENV_PATH/bin/python

cd "$SCRIPT_PATH"

pip install django gunicorn

python manage.py migrate

python manage.py collectstatic --noinput

mkdir logs
mkdir $SCRIPT_PATH/systemd
echo "
[Unit]
Description=SpinBotAdmin Gunicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$SCRIPT_PATH
ExecStart=$ENV_PATH/bin/gunicorn \
        --workers 3 \
        --bind unix:$SCRIPT_PATH/gunicorn/gunicorn.sock SpinBot.wsgi:application  \
        --access-logfile $SCRIPT_PATH/gunicorn/access.log \
        --error-logfile $SCRIPT_PATH/gunicorn/error.log 
Restart=always

[Install]
WantedBy=multi-user.target
" | tee $SCRIPT_PATH/systemd/spinbotadmin.service

echo "
[Unit]
Description=SpinBot Gunicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$SCRIPT_PATH
ExecStart=$PYTHON $SCRIPT_PATH/manage.py tg_bot
Restart=always

[Install]
WantedBy=multi-user.target
" | tee $SCRIPT_PATH/systemd/spinbot.service

sudo systemctl disable spinbotadmin.service spinbot.service
sudo systemctl enable $SCRIPT_PATH/systemd/spinbot.service $SCRIPT_PATH/systemd/spinbotadmin.service

mkdir $SCRIPT_PATH/nginx
echo "
server {
    listen 80;
    server_name $(curl https://icanhazip.com/);

    location / {
        proxy_pass http://unix:$SCRIPT_PATH/gunicorn/gunicorn.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias $SCRIPT_PATH/static/;
    }

    location /media/ {
        alias $SCRIPT_PATH/media/;
    }
}
" | tee $SCRIPT_PATH/nginx/spinbot.conf

sudo rm /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/spinbot.conf

sudo ln -s $SCRIPT_PATH/nginx/spinbot.conf /etc/nginx/sites-enabled/

sudo sed -i 's/user www-data;/user ubuntu;/' /etc/nginx/nginx.conf

sudo nginx -t

sudo service nginx restart

python manage.py fill_combs
