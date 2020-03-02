from mysql_credentials import MysqlCredentials as dbc

SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{dbc.user}:{dbc.password}@localhost/sqlalchemy_flask'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
