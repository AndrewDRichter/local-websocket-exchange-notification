# Local Websocket project: Exchange Notificator
This is a project i made for the company i work. Basically, the exchange value used in daily financial operations was sent through whatsapp in a private group for the customer service team.
It works fine for the size of the company and the operations we deal with. But when someone needed to take a look at the current exchange they had to open his whatsapp and take a look on that group.
Most of the time it doesn't bother in any way, but depending on the situation, like, slow services or in a hurry, it could lead to a misinformation or, using the last exchange value and not the updated one.
And so, this idea was born. A simple API + a simple websocket service + a simple client, that could be lightweight and could easily be installed on the users machine, running in local network.

# Installation
Clone the repo
```bash
git clone https://github.com/AndrewDRichter/local-websocket-exchange-notification.git
```
Create and activate a virtual environment
```bash
python -m venv env
env\Scripts\activate
```
Install the dependencies
```bash
pip install -r requirements.txt
```

# Project setup
Change the server ip in the client.py file to your servers ip
```python
uri = "ws://192.168.1.140:8000/ws" # change to ws://YOUR_PC/SERVER_IP:8000/ws
```
Run the pyinstaller to generate the server and client .exe files
```bash
pyinstaller --onefile --noconsole server.py
pyinstaller --onefile --noconsole client.py
```

# API and client usage
The generated .exe files are in the projects directory > dist folder.
Now you can run the server + client files (following this order).
Access the exchange API in the browser http://localhost:8000/docs.
There you can change the exchange and see the results in the system tray, there will be an icon of the client app.
If you do a right-click with the mouse you will see the new exchange you setup in the API.

# Thank you!
Thank you for your time, you are free to clone or fork this project!
You are free to give me any feeback!
