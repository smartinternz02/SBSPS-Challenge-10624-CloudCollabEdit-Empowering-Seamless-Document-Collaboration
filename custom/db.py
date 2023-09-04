import ibm_db
from .config import DB2_DATABASE, DB2_HOST, DB2_PASSWORD, DB2_PORT, DB2_USERNAME

def db_connect():
    conn_str = f'DATABASE={DB2_DATABASE};HOSTNAME={DB2_HOST};PORT={DB2_PORT};SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID={DB2_USERNAME};PWD={DB2_PASSWORD};'
    conn = ibm_db.connect(conn_str, '', '')
    print("Connected Successfully...")
    return conn