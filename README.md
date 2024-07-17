# Chess Game
This project allows for multiple people to play chess using a client-server model. It is built in Python using the socket and threading modules, which allow for many games to run concurrently.


Features
- Encodes all standard chess rules, such as en passant and castling.
- Clients handle game state logic, show available moves, and test for checkmate.
- Servers match clients into games, send moves between them, and notify clients if their opponent was disconnected.


How to Run
- Clone the repository
- Fill in the server's host and port in server.py and client.py
- Start the server on one device by running "python server.py"
- For each client run the main.py script with the command "python main.py"
