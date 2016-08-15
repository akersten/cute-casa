#!/bin/bash

# Kill script for cleaning up the local CuteCasa instance. Deletes the local secret directories containing the database
# as well as the compiled CSS files.

rm -rf config/secret
rm -rf test/secret
rm -f static/css/bin/cutecasa.css
rm -f static/css/bin/cutecasa.css.map
rm -f static/css/bin/cutecasa-splash.css
rm -f static/css/bin/cutecasa-splash.css.map
rm -f init.sh
rm -f run.sh