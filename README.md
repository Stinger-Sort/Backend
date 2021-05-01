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
MAIL_PASSWORD = 'password'
DB_BIND = 'postgres://postgres:postgres@localhost/postgres'
UPLOAD_FOLDER = '/home/user/upload'
```
