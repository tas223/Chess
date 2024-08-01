# Chess Game
This project allows for multiple people to play chess using a client-server model. It is built in Python using the socket and threading modules, which allow for many games to run concurrently.

<br>

Features
- Encodes all standard chess rules, such as en passant and castling.
- Clients handle game state logic, show available moves, and test for checkmate.
- Servers match clients into games, send moves between them, and notify clients if their opponent was disconnected.

<br>

How to Run
- Clone the repository
- Fill in the server's host and port in server.py and client.py
- Start the server on one device by running "python server.py"
- For each client run the main.py script with the command "python main.py"

<br>

Example Game Run 
- User clicks join game button and then stays on the waiting screen until an opponent is found.
- During the game, the last move is shown with a purple background, and a piece's valid moves are shown with a green background.
- When the game ends, the user is told why the game ended and is then redirected back to the home screen.

<img width="400" height="400" alt="JoinGame" src="https://github.com/user-attachments/assets/63a696f8-a769-47ab-b784-673b1d8a77b8">
<img width="400" height="400" alt="WaitingScreen" src="https://github.com/user-attachments/assets/c6e1ff7c-0c68-4869-bebc-d0ab19431db1">
<img width="400" height="400" alt="ExampleGame" src="https://github.com/user-attachments/assets/d0900e6b-7cef-420c-90a3-3c75fd2464ce">
<img width="400" height="400" alt="WinScreen" src="https://github.com/user-attachments/assets/5f65727a-4a12-44bb-a1e9-72178aee95e9">

