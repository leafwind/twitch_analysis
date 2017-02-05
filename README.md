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

## log

/var/log/nginx/error.log

## restart

sudo service nginx restart
