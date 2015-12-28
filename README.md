# cute-casa
A centralized home management system; rent payment/lease administration, IoT integration, maintenance reminders, dashboards

See the splash page at [http://cute.casa](http://cute.casa).

## Overview

CuteCasa is a self-hosted house administration system. Through online dashboards, you can control every aspect of your
IoT-enabled house, split bills, manage rent, delegate tasks, and more.

## Technologies

* jQuery
* Flask
* Bootstrap
* Sass

## Setup

Being a self-hosted solution, you'll need to run this on your own equipment. The cute.casa website is intended for
future paid/dedicated hosting.

### Requirements

* Python (3.4+)
* Flask
* ZODB

### Running CuteCasa

Create a shell script to load the variables in cute.py and to launch the program:

    #!/bin/sh
    export CUTE_DB="secret/cute.db"
    export CUTE_DEBUG="False"
    export CUTE_SECRET_KEY="set a secret development key"
    export CUTE_USERNAME="admin"
    export CUTE_PASSWORD="set a secret password"
    export CUTE_PORT="5050"
    export CUTE_SALT="16 or so good random bytes"
    python3 cute.py

Set it executable (`chmod +x cute.sh`) and run it (`./cute.sh`). If everything's set up correctly, CuteCasa will now be
running on your server. Obviously don't commit this file into VCS.

## Contributors

[Alex Kersten](http://kersten.email)
