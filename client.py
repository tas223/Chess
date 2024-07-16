import pickle
import socket


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = "localhost"
        self.port = 9593
        self.player = self.connect()
        self.client.settimeout(1.0)

    def connect(self):
        try:
            self.client.connect((self.ip, self.port))
            return int(self.client.recv(5).decode())
        except socket.error as e:
            print(e)
        except UnicodeDecodeError as e:
            print(e)

    def getPlayerNumber(self):
        return self.player

    def send(self, board):
        try:
            self.client.send(pickle.dumps(board))
        except socket.error as e:
            print(e)

    def receive(self):
        try:
            data = self.client.recv(4096)
            if data:
                return pickle.loads(data)
            return None
        except socket.timeout:
            return None
        except socket.error as e:
            print(e)

    def close(self):
        self.client.close()
