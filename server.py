import socket
from _thread import *
import pickle
import threading

HOST = "localhost"
PORT = 9593

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Server has been started. Waiting for connection.")

player = -1
games = {}
waiting = []
threadingLock = threading.Lock()


def handleClient(connection):
    global player, waiting
    player = (player + 1) % 2
    connection.send(str(player).encode())

    with threadingLock:
        if not waiting:
            waiting.append(connection)
        else:
            opponent = waiting.pop()
            games[connection] = opponent
            games[opponent] = connection
            connection.send(pickle.dumps("start"))
            opponent.send(pickle.dumps("start"))

    while True:
        try:
            data = connection.recv(4096)
            if data:
                games[connection].send(data)
            elif not data:
                print("Player disconnected")
                if connection in games and games[connection] in games:
                    games[connection].send(pickle.dumps([(1, 1)]))
                break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

    with threadingLock:
        if connection in waiting:
            waiting.remove(connection)
        if connection in games:
            del games[connection]
    connection.close()


while True:
    connection, address = server.accept()
    start_new_thread(handleClient, (connection,))
