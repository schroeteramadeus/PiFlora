# PyPlant
## Overview
Backend: Webserver implemented via Python HTTPServer, miflora framework, self coded framework for wrapping and other hardware support (e.g gpio pumps)

Frontend: Standard HTML, CSS, JS utilizing ajax for data polling and simple configuration of the backend

For (normal) use on a linux environment with enabled bluetooth and miflora plant sensors. Preferable is raspberry pi (3) for gpio and additional hardware support.

WARNING: Debug mode will trigger on ALL other systems - (on the webpage) descernable by the multicolored yellow status bar on the services (e.g red-yellow), see help page for more info

### Example software setup

- install raspberry pi os

- install python (3.*)

- install (via pip) miflora

- make sure bluetooth is available (especially the command "sudo hcitool lescan")

### Example hardware setup 1

- raspberry pi (3)

- miflora plant sensor

TODO add image of setup

### Example hardware setup 2

- raspberry pi (3)

- miflora plant sensor

- relais (5v)

- pumps (12v) with adequate piping

- water reservoir

- 5v (for relais to use with jumper) and 12v (for pumps) batteries

- dont forget the cables, boards, etc.

TODO add image of setup

## Configuration via web

TODO
