import socket
from threading import Thread
import sys
import os

import base64
import hashlib
import struct
import handler

# ====== config ======


MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
                   "Upgrade:websocket\r\n" \
                   "Connection: Upgrade\r\n" \
                   "Sec-WebSocket-Accept: {1}\r\n" \
                   "WebSocket-Location: ws://{2}/chat\r\n" \
                   "WebSocket-Protocol:chat\r\n\r\n"


class Th(Thread):
    def __init__(self, sock, buf):
        super(Th, self).__init__()
        self.con = sock
        self.buf = buf

    def run(self):
        while True:
            data = self.recv_data(self.buf)
            #data = self.con.recv(self.buf)
            print 'Received data:'
            print data
            print handler.stat_dict
            handler.update_stat_dict(data, handler.stat_dict)
            print handler.stat_dict
            handler.drive_car(handler.stat_dict)

        self.con.close()

    def recv_data(self, num):
        try:
            all_data = self.con.recv(num)
        except Exception as e:
            print e
            return False

        if not len(all_data):
            return False
        else:
            code_len = ord(all_data[1]) & 127
            if code_len == 126:
                masks = all_data[4:8]
                data = all_data[8:]
            elif code_len == 127:
                masks = all_data[10:14]
                data = all_data[14:]
            else:
                masks = all_data[2:6]
                data = all_data[6:]
            raw_str = ""
            i = 0
            for d in data:
                raw_str += chr(ord(d) ^ ord(masks[i % 4]))
                i += 1
            return raw_str

    # send data
    def send_data(self, data):
        if data:
            data = str(data)
        else:
            return False
        token = "\x81"
        length = len(data)
        if length < 126:
            token += struct.pack("B", length)
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)

        data = '%s%s' % (token, data)
        self.con.send(data)
        return True

# handshake
def handshake(con):
    headers = {}
    shake = con.recv(1024)
    if not len(shake):
        return False
    header, data = shake.split('\r\n\r\n', 1)
    for line in header.split('\r\n')[1:]:
        key, val = line.split(': ', 1)
        headers[key] = val
    if 'Sec-WebSocket-Key' not in headers:
        print ('This socket is not websocket, client close.')
        con.close()
        return False
    sec_key = headers['Sec-WebSocket-Key']
    res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())
    str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', host + ':' + str(port))
    print str_handshake
    con.send(str_handshake)
    return True


def new_service(host, port, buf):
    """start a service socket and listen
    when coms a connection, start a new thread to handle it"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        sock.listen(5)

        print "Bing port {port}, wait for connection".format(port=port)
    except Exception as e:
        print e
        print("Server is already running,quit")
        sys.exit()

    while True:
        connection, address = sock.accept()

        print "Got connection from ", address
        #if True: # debug
        if handshake(connection):
            print "handshake success"
            try:
                t = Th(connection, buf)
                t.start()
                print 'new thread for client ...'
            except:
                print 'start new thread error'
                connection.close()


if __name__ == '__main__':
    host = '192.169.173.11'
    port = 9999
    buf = 1024
    new_service(host, port, buf)