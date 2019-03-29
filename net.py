import threading
import time
import socket
import json
import os
import struct
import subprocess
from strings import chunkstring
from sys     import exit
import sys

def connecter_server(HOST, PORT):
    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            s = None
            continue
        try:
            s.bind(sa)
            s.listen(100)
        except socket.error as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print("Could not open socket")
        exit(1)
    else:
        return s

def connector_client(addr, port):
    s = None
    for res in socket.getaddrinfo(addr, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            s = None
            continue
        try:
            s.connect(sa)
        except socket.error as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print("[ WAR ]: Could not open socket")
        return "offline"
    else:
        return s

class NetworkHandler:
    def __init__(self, addr, port):
        self.addr = (addr, port)
        self.s = connector_client(addr, port)
        if self.s == "offline":
            print("[ ERR ]: No route to server")
            print("[ INF ]: Starting internal server")
            self.offline = True
            self.server_thread = threading.Thread(target=self.server_listner)
            self.server_thread.start()
            time.sleep(0.8)
            self.s = connector_client(addr, port)
        else:
            self.offline = False

    def server_listner(self):
        s = connecter_server(self.addr[0], self.addr[1])
        conn, addr = s.accept()

        self.con = Connection(conn)
        self.con.run()
        
    def send_data(self, data):
        #time.sleep(0.5)
        string = json.dumps(data)
        string = struct.pack('>I', len(string.encode("utf-8"))) + string.encode("utf-8")
        self.s.sendall(string)

    def recv_data(self):
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        s = self.recvall(msglen).decode("utf-8")
        return json.loads(s)

    def recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.s.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def close(self):
        self.s.close()
        if self.offline:
            self.con.exit_()
    
class Connection(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.s = conn
        self.exit = False
        self.proc_out = ""

    def send_data(self, data):
        string = json.dumps(data)
        string = struct.pack('>I', len(string.encode("utf-8"))) + string.encode("utf-8")
        self.s.sendall(string)

    def recv_data(self):
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return json.loads(self.recvall(msglen).decode("utf-8"))

    def recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.s.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def exit_(self):
        self.exit = True

    def run_file(self):
        self.proc = subprocess.Popen(['python3', "-u", self.current_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = self.proc.stdout.readline() + self.proc.stderr.readline()
            if output == b'' and self.proc.poll() is not None:
                break
            if output:
                print(output.decode("utf-8"))
                self.proc_out += output.decode("utf-8")
            rc = self.proc.poll()
        print("PROC-OUT:", self.proc_out)
        self.send_data({"print": self.proc_out})
        
    def run(self):
        try:
            while not self.exit:
                data = self.recv_data()
                #print(data)
                if data == None:
                    break

                elif data["request"] == "rename_file":
                    os.rename("." + data["from"], data["to"])
                    
                elif data["request"] == "list":
                    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames]
                    self.send_data({"result": result})

                elif data["request"] == "get_file":
                    try:
                        with open("." + data["value"], "r") as f:
                            self.send_data({"result": f.read(), "status": 0})
                    except Exception as e:
                        self.send_data({"status": str(e)})

                elif data["request"] == "write_file":
                    with open("." + data["file"], "w") as f:
                        f.write(data["value"])

                elif data["request"] == "run":
                    self.current_file = "." + data["value"]
                    self.proc_out = ""
                    try:
                        self.exec_thread = threading.Thread(target=self.run_file)
                        self.exec_thread.start()
                    except IOError:
                        self.send_data({"print": "Error - file not found"})

                elif data["request"] == "stop":
                    self.proc.kill()
        finally:
            time.sleep(1)
            self.s.close()
