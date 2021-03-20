# IRIB_FollowUpProject

1- apt-get update && apt-get -y upgrade
2- apt-get install python3 && apt-get install python3-pip && apt-get install libpq-dev
3- Install nginx:

    sudo apt-get install nginx

4- sudo pip3 install virtualenv
5- Create virtual environment: virtualenv venv
6- Clone source: sudo git clone https://github.com/aallli/IRIB_FollowUpProject.git
7- Activate virtualenv: source venv/bin/activate
8- pip install -r requirements.txt

NOTE: If pyodbc installation failed, install unixodbc-dev:

    sudo apt-get install unixodbc-dev
    
9- Install postgresql:

    sudo apt-get install postgresql postgresql-contrib
    sudo usermod -aG sudo postgres

10- Switch over to the postgres account on your server by typing:
    
    sudo -i -u postgres

11- Create database named sadesa: sudo -u postgres createdb

    sudo -u postgres createdb irib_followup

12- Set postgres password: 
    
    sudo -u postgres psql postgres
    \password postgres
    \q
    exit    E|r|bF0ll0wup

13- Caution: Allow remote access to postgres:
    
    Add to /etc/postgresql/9.5/main/postgresql.conf : #listen_addresses = '*'
    Add to /etc/postgresql/9.5/main/pg_hba.conf : host all all 0.0.0.0/0 trust
    systemctl restart postgresql

14- Set environment variable for database access: 

    export DATABASES_PASSWORD='[Database password]'

15- python manage.py migrate

NOTE: Set environment variable for database access: 

    export ALLOWED_HOSTS='[Server IP]'
    
16- test if gunicorn can serve application: gunicorn --bind 0.0.0.0:8000 IRIB_FollowUpProject.wsgi
17- sudo groupadd --system www-data
18- sudo useradd --system --gid www-data --shell /bin/bash --home-dir /home/[user]/followup/IRIB_FollowUpProject followup
19- sudo usermod -aG sudo followup
20- sudo chown -R qbesharat:www-data /home/[user]/followup/IRIB_FollowUpProject
21- sudo chmod -R g+w /home/[user]/followup/IRIB_FollowUpProject
22- sudo chmod 777 /home/[user]/followup/IRIB_FollowUpProject/media/

Configure Gunicorn:
23- sudo nano /etc/systemd/system/gunicorn-followup.service
24- add:
    
    [Unit]
    Description=gunicorn daemon
    After=network.target
    
    [Service]
    User=qbesharat
    Group=www-data
    WorkingDirectory=/home/[user]/followup/IRIB_FollowUpProject
    EnvironmentFile=/etc/gunicorn-followup.env
    ExecStart=/home/[user]/followup/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/[user]/followup/IRIB_FollowUpProject/IRIB_FollowUpProject.sock IRIB_FollowUpProject.wsgi:application
    
    [Install]
    WantedBy=multi-user.target
        
25- sudo nano /etc/gunicorn-followup.env
26- Add followings:
    
    DEBUG=0
    DEPLOY=1
    ALLOWED_HOSTS='[server ip]'
    ADMIN_TEL='[admin tel]'
    ADMIN_EMAIL='[admin email]'
    LIST_PER_PAGE=[list per page in admin pages]
    ACCESS_PERSONNEL_DATABASES_URL=[personnel access database url]
    
27- sudo systemctl start gunicorn-followup
28- sudo systemctl enable gunicorn-followup
29- Check if 'IRIB_FollowUpProject.sock' file exists: ls /home/[user]/followup/IRIB_FollowUpProject
30- sudo nano /etc/nginx/conf.d/proxy_params
31- Add followings:

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

32- If gunicorn.service file is changed, run:

    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn-qbesharat

33- Install gettext:

    deactivate
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install
    sudo apt-get install gettext

34- Compile messages for i18N:
    
    source env/bin/activate
    django-admin compilemessages -f (if translation is needed)

35- Collect static files: (Create static and uploads directory if needed)
 
    python manage.py collectstatic

Configure Nginx:
36- create keys and keep them in /root/certs/qbesharat/:
    
    openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out /root/certs/followup/followup.crt -keyout /root/certs/followup/followup.key

37- Restrict the key’s permissions so that only root can access it:
    
    chmod 400 /root/certs/followup/followup.key


38- Run nginx:

    sudo systemctl daemon-reload
    sudo systemctl start nginx.service
    sudo systemctl enable nginx.service
    
39- Configure nginx:

    sudo nano /etc/nginx/conf.d/followup.conf

40- Add:
    
    server {
        listen       80;
        server_name  office.eirib.ir;
    
        error_page 404 /404.html;
        location /404.html {
            root /home/[user]/followup/IRIB_FollowUpProject/static/errors;
            internal;
        }
    
        location /static/ {
            if ($request_method = 'GET') {
                add_header 'Access-Control-Allow-Origin' 'http://office.eirib.ir:8000';
                add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS';
                add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
                add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
            }
    
            root /home/[user]/followup/IRIB_FollowUpProject;
        }
    
        location   / {
            return 301 http://office.eirib.ir:8000;
        }
    }
    
    server {
        listen 8000;
        server_name  office.eirib.ir;
    
        location = /favicon.ico { access_log off; log_not_found off; }
    
        error_page 502 /502.html;
        location /502.html {
            root /home/[user]/followup/IRIB_FollowUpProject/static/errors;
            internal;
        }
    
        error_page 503 504 507 508 /50x.html;
        location /50x.html {
            root /home/[user]/followup/IRIB_FollowUpProject/static/errors;
            internal;
        }
    
        location /static/ {
            root /home/[user]/followup/IRIB_FollowUpProject;
        }
    
        location /media/ {
            root /home/[user]/followup/IRIB_FollowUpProject;
        }
    
        location / {
            include proxy_params;
            proxy_pass http://unix:/home/[user]/followup/IRIB_FollowUpProject/IRIB_FollowUpProject.sock;
        }
    }

41- Test your Nginx configuration for syntax errors by typing: 

    sudo /usr/sbin/nginx -t

42- Restart nginx:

    sudo systemctl restart nginx.service
    sudo systemctl status nginx.service

43- Get more admin themes:
    
    python manage.py loaddata admin_interface_theme_django.json
    python manage.py loaddata admin_interface_theme_bootstrap.json
    python manage.py loaddata admin_interface_theme_foundation.json
    python manage.py loaddata admin_interface_theme_uswds.json