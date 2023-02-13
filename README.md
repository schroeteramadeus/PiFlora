# PyPlant
## Overview
Backend: Webserver implemented via Python HTTPServer, miflora framework, self coded framework for wrapping and other hardware support (e.g gpio pumps)

Frontend: Standard HTML, CSS, JS utilizing ajax for data polling and simple configuration of the backend

For (normal) use on a linux environment with enabled bluetooth and miflora plant sensors. Preferable is raspberry pi (3) for gpio and additional hardware support.

WARNING: Debug mode will trigger on ALL other systems for bluetooth manager and on systems that do not have miflora installed for the plant manager - (on the webpage) descernable by the multicolored yellow status bar on the services (e.g red-yellow), see help page for more info

### Example software setup

- install raspberry pi os

- install python (3.*)

- install (via pip) miflora

- (optionally) install (via pip) pyOpenSSL (though you can still run on http or put your custom certificate and key in the designated folder)

- make sure bluetooth is available (especially the command "sudo hcitool lescan")

### Run the web server

- python3 startWebserver.py

- optionally for startWebserver.py you can also define  -www [HTML folder path], -save [save folder path], -sslCert [ssl certificate path], -sslKey [ssl private key path]

- for a full list of editable configurations (that are run on startup when no parameters are given), feel free to change them in the Config/Config.py file

### Troubleshooting

- if you are running on https, make sure the certificate is registered on your client

- if you are not running on localhost (127.0.0.1), make sure your firewall does not block incoming/outgoing requests on the specified port

### Example hardware setup (simplest)

- raspberry pi (3)

- miflora plant sensor

TODO add image of setup

### Example hardware setup (advanced)

- raspberry pi (3)

- miflora plant sensor

- relais (5v)

- pumps (12v) with adequate piping

- water reservoir

- 5v (for relais to use with jumper) and 12v (for pumps) batteries

- dont forget the cables, boards, etc.

TODO add image of setup

## Configuration via web

- Start the webserver on via "python3 startWebserver.py"

- Put in the working directory "www"

- For the saving location you can just press enter

- open your webbrowser and either use [your ip adress or localhost]:8080

- if you encounter non-trivial problems consult the help page

NOTE: on debug mode the server will NOT save any changes after it was closed, also in order to change, add or delete plants the plant manager needs to be stopped first
