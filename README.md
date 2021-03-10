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