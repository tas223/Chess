import pickle
import socket


class Client:
    """
        Establishes methods for client socket to connect to server, send/receive information, and close.
        Initialized with a timeout so that the blocking behavior won't prevent user from  exiting game.
        Send and receive methods use pickle for serialization because data type is list of tuples.
    """

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = "localhost"  # Fill in with server's ip and port
        self.port = 9593
        self.connected = self.connect()
        self.client.settimeout(1.0)

    def connect(self):
        """ 
        Connects to server and main.py uses return value to choose next course of action

        Returns:
            int: returns 1 if client will join game and 0 if server can't accept client or connection fails
        """
        try:
            self.client.connect((self.ip, self.port))
            return int(self.client.recv(5).decode())
        except socket.error as e:
            print(e)
            return 0
        except UnicodeDecodeError as e:
            print(e)
            return 0

    def validConnection(self):
        return self.connected

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
