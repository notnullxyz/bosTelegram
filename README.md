# bosTelegram chat server with built in client
Bos Telegram, afrikaans meaning "bush telegram", is an old phrase referring to gossip or inaccurate news moving between the people. You heard it on the bush telegram, ey?
This is a simple, non-secure, non-private chat server that you can run anywhere you have Python, really. The interface for the client is served on calling your server root URL in a browser.
It's simple, old-school, and does the job for a project I created it for. It's not an ircd, and it's not related to Telegram. Telegram is actually a word, referring to something much older than the Telegram network/app.

The Project Structure

BosTelegram/
├── bosServer.py
├── bosTelegram.cfg
├── db/
│   └── chats.db
└── README.md (this file)

![image](https://github.com/user-attachments/assets/5626e50d-c851-4626-bfdb-cf081df8d421)

## Deployment Information
* Python Version: This code requires Python 3.x.
* Dependencies: Ensure you have Flask installed. You can install it using ```pip install flask```
* Database: The server uses SQLite as the database, which is a flat-file database and works out of the box with Python.

### Running the Server:
* Ensure the bosTelegram.cfg configuration file is in the same directory as bosServer.py
* Change the config as you see fit.
* Run the server using the command ```python3 bosServer.py```
* The server will listen on ```0.0.0.0:8100``` by default, which allows it to be accessible from any network interface.
* Access it from a browser, somewhere. http://your server ip:port/
