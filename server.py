import socket
from _thread import *
import pickle
import threading


# When updating the HOST and PORT constants, also change client.py
HOST = "localhost"
PORT = 9593


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)
print("Server has been started. Waiting for connection.")

"""
    Games dictionary stores each client connection and opponent for current games.
    Waiting list stores a client until someone else joins to play against them.
    currentConnections stores the number of active connections and won't allow for more than 10 simultaneous games.
    threadingLock prevents errors by only allowing one thread to access shared resources at a time.
"""
games = {}
waiting = []
currentConnections = 0
threadingLock = threading.Lock()


def handleClient(connection):
    """
        handleClient first sends 1 to the client connection, signaling a successful connection to the server.
        Then, the connection is either added to waiting or is matched to an opponent in waiting. 
        Matched players are sent opposing numbers that tell main.py which player the user is and that the game has started.
        While the player sends a last move, forward that data to its opponent, and if a user disconnects, notify their opponent.
        Remove the user's presence from games/waiting, decrement current connections, and close their socket.
    """
    global games, waiting, currentConnections
    connection.send(str(1).encode())

    with threadingLock:
        currentConnections += 1
        if not waiting:
            waiting.append(connection)
        else:
            opponent = waiting.pop()
            games[connection] = opponent
            games[opponent] = connection
            connection.send(pickle.dumps("1"))
            opponent.send(pickle.dumps("0"))

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
        currentConnections -= 1
        if connection in waiting:
            waiting.remove(connection)
        if connection in games:
            del games[connection]

    connection.close()


"""
    Continuously accepts new connections and starts a separate thread for each one until reaching 20 active connections.
    Sends 0 to client socket if connection limit is reached. Closes server socket at the end.
"""
try:
    while True:
        connection, address = server.accept()
        if currentConnections >= 20:
            connection.send(str(0).encode())
            connection.close()
            continue
        start_new_thread(handleClient, (connection,))
finally:
    server.close()
