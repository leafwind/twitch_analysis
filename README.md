# prerequest

sudo apt-get install g++

# setup document

[How To Serve Flask Applications with uWSGI and Nginx on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04)

# uwsgi

## Upstart Script

`/etc/init/twitch_analysis.conf`

`sudo start twitch_analysis`

## log location

/var/log/uwsgi/uwsgi.log

## debug

when finished modifying the code, run

run `sudo restart twitch_analysis`

run `sudo tail -f /var/log/uwsgi/uwsgi.log` in another screen

# nginx

usually no need to care about nginx unless there are traffic/connection issues.

## setup

`sudo cp twitch_analysis.conf /etc/nginx/sites-available/twitch_analysis`

### ACME (Automatic Certificate Management Environment)

[acme-nginx](https://github.com/kshcherban/acme-nginx)

## debug

### HTTP 400

check if all conf has been correctly set
* `ipv6only=on` is must, otherwise it will listen twice for the same port
e.g. `listen [::]:443 ssl ipv6only=on default_server;`

* Don't include `ssl on;`

### conflicting server name "bot.leafwind.tw" on 0.0.0.0:80, ignored
check if `/etc/nginx/sites-available/twitch_analysis~` exists

## log

/var/log/nginx/error.log

## conf

`sudo vim /etc/nginx/nginx.conf`
`sudo vim /etc/nginx/sites-available/twitch_analysis`

## restart

sudo service nginx restart
