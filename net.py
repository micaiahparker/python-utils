try:
    import rsa
except:
    print("You cannot use this without the rsa module.")
    print("To install this, run 'pip install rsa'.")
    exit(-1)

import socket

key_request = "Requesting key".encode('utf-8')
end_of_message = "End of message".encode('utf-8')


class secureSocket(socket.socket):
    def __init__(self, keysize=1024, *args, **kargs):
        if kargs.get('keysize'):
            keysize = kargs.pop('keysize')
        self.sock = socket.socket(*args, **kargs)
        self.conn = None
        self.pub, self.priv = rsa.newkeys(keysize)
        self.keysize = keysize
        self.key = None

    def connect(self, ip):
        self.sock.connect(ip)
        self.conn = self.sock

    def close(self):
        self.conn.close()
        self.conn = None

    def accept(self):
        self.conn, self.addr = self.sock.accept()

    def bind(self, *args):
        self.sock.bind(*args)

    def listen(self, i):
        self.sock.listen(i)

    def settimeout(self, i):
        self.sock.settimeout(i)
        self.conn.settimeout(i)

    def send(self, msg):
        while self.key is None:
            print("Key not found. Requesting key")
            self.conn.send(key_request)
            try:
                key = self.conn.recv(keysize).split(",")
                self.key = rsa.PublicKey(int(key[0]), int(key[1]))
                print("Key received")
            except EOFError:
                continue
        if not isinstance(msg, type("a".encode('utf-8'))):
            msg = msg.encode('utf-8')
        x = 0
        while x < len(msg) - 117:
            self.conn.sendall(rsa.encrypt(msg[x:x+117], self.key))
            x += 117
        self.conn.sendall(rsa.encrypt(msg[x:], self.key))
        self.conn.sendall(rsa.encrypt(end_of_message, self.key))

    def recv(self):
        received = "".encode('utf-8')
        a = ""
        try:
            while True:
                a = self.conn.recv(128)
                if a == key_request:
                    print("Key requested. Sending key")
                    self.conn.sendall((str(self.pub.n) + "," + str(self.pub.e)).encode('utf-8'))
                    continue
                a = rsa.decrypt(a, self.priv)
                if a == end_of_message:
                    return received
                received += a
        except rsa.pkcs1.DecryptionError as error:
            print("Decryption error---Content: " + str(a))
            return "".encode('utf-8')
