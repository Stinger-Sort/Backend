import pymysql.cursors
import config

connection = pymysql.connect(
    host='localhost',
    user=config.db_login,
    password=config.db_password,
    database='db',
    cursorclass=pymysql.cursors.DictCursor
)