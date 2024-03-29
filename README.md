# PiFlora
## Disclaimer
The code in this repository is currently NOT finished and could contain bugs, unfinished functionalities and generally unexpected behaviour. The project is mainly developed for research purposes and personal usage, as such it will probably not be updated frequently. Feel free to contribute or fork.

## Overview

Web-based management / automation software solution for managing plants via a Raspberry Pi, sensors, pumps, etc..

Backend: Webserver implemented via Python HTTPServer, miflora framework, self coded framework for wrapping and other hardware support (e.g. gpio pumps)

Frontend: Vue and standard HTML, CSS, JS utilizing ajax for data polling and simple configuration of the backend

For (normal) use on a linux environment with enabled bluetooth and miflora plant sensors. Preferably deployed on raspberry pi (3) for gpio and additional hardware support.

WARNING: Debug mode will trigger on ALL other systems for bluetooth manager and on systems that do not have miflora installed for the plant manager - (on the webpage) descernable by the multicolored yellow status bar on the services (e.g red-yellow), see help page for more info

## Example Setup

### Example software setup

- install raspberry pi os

- install python (3.*)

- install (via pip) miflora

- install npm

- (optionally) install (via pip) pyOpenSSL (though you can still run on http or put your custom certificate and key in the designated folder)

- make sure bluetooth is available (especially the command "sudo hcitool lescan")


### Example hardware setup (simplest)

- linux pc

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

## Using the system

### Run the web server

- <code>python3 startWebserver.py</code>

- for testing use the <code>-debug</code> flag (no tsl and save files, modules will be run in debug mode), but keep in mind that if not set some functionalities may still run on debug mode (e.g. bluetooth on a non-linux os)

- use the <code>-rebuild</code> flag, if <code>npm run build</code> should be excecuted, note that if the vue/dist directory does not exists, it will be build anyways

- optionally for startWebserver.py you can also define  <code>-www [HTML folder path]</code>, <code>-save [save folder path]</code>, <code>-sslCert [ssl certificate path]</code>, <code>-sslKey [ssl private key path]</code>

- for a full list of editable configurations (that are run on startup when no parameters are given), feel free to change them in the config/server.conf file (will be created on first run)

### Troubleshooting

- if you are running on https, make sure the certificate is registered on your client (trusted)

- if you are not running on localhost (127.0.0.1), make sure your firewall does not block incoming/outgoing requests on the specified port

- if you encounter non-trivial problems consult the help page
