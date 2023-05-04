# ScreenController
Server and app to controll a desktop by an mobile devide or another desktop. Just works in local connections.  
This programs had some vulnerabilities so **DON`T USE IN OPEN NETWORKS** or anyone in the network can see your screen bruteforcing the key

## Dependencies
This project uses some python libs, to install then execute the follow commands:
```
pip install Flask Flask-Cors numpy opencv-python websockets PyAutoGUI asyncio mss
```

## How to use:
### Note about screen selection
The script are set to capture a second screen on the left of the main screen, if you want to another screen 
 - Change the `bounding_box` top and left selecting the correct screen
 - Change the math in the `pyautogui.moveTo()` inside the handler function
### Runing the server
Execute the [open_servers.py](https://github.com/EduardoPortoSilva/ScreenController/blob/main/server/open_servers.py), the script will prompt for some parameters

 - If your computer had more than one IPV4 will ask you which one to use
 - The resolution to capture in the screen
 - If you want to pad the capture, if so will ask the padding size
 - The key to connect to the servers, this will works like a password in the client (You can just leave it empty if dont want to protect by that)

After setting the parameters both servers will be open

### Runing the client
If you want to control by a web browser just open the [index.html](https://github.com/EduardoPortoSilva/ScreenController/blob/main/web%20client/index.html) insert the IP you set in the server, leave the ports as is, insert the key and click in connect

If you want to control by a mobile device download the [APK](https://github.com/EduardoPortoSilva/ScreenController/blob/main/android%20client/APK/app.apk) (Or download the project and compile that in your computer) and install.  
When you open it insert the IP you set in the server, leave the ports as is, insert the key and click in connect
If when you try to connect it show just a white screen it means the client can`t connect to the server
