Install
```console
pip install virtualenv
virtualenv env
env/Scripts/activate.ps1
pip install -r requirements.txt
```

```console
touch config.py
```

```python
# config.py
login = 'postgres'
password = 'password'
database = 'postgres'
host = '127.0.0.1'
```

```console
export MAIL_SERVER=smtp.googlemail.com
export MAIL_PORT=5000
export MAIL_USE_TLS=1
export MAIL_USERNAME=sort.app.yar
export MAIL_PASSWORD=<your-gmail-password>
```