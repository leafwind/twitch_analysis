# Twitch Analysis Backend

A Flask application.

Data processing by pandas, stored by sqlite3.

# Package Requirements

`sudo apt-get install g++`

```
virtualenv __
. __/bin/activate
pip install requirements.txt
```

# Deploy the code change

`sudo systemctl restart twitch_analysis_uwsgi`
`tail -f /var/log/uwsgi/uwsgi.log`
