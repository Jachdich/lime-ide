from net import Connection, connecter_server as connecter
from sys import exit
import constants

HOST = None
PORT = constants.PORT

s = connecter(HOST, PORT)

con = []
try:
    while True:
        conn, addr = s.accept()
        #print("Connected by", addr)

        con.append(Connection(conn))
        con[-1].start()
except KeyboardInterrupt:
    quit()
finally:
    quit()

def quit():
    global conn
    for i in con:
        i.join()
    conn.close()
