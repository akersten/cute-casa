#!/bin/sh

# Build script to get cutecasa ready. The build script should be non-destructive (in contrast with the init script).

clear

echo "CuteCasa build started..."

echo "  Building stylesheets..."

if  [ ! -d static/css/bin ]
then
    mkdir static/css/bin
fi
sass src/scss/bulma.scss static/css/bin/bulma.css
sass src/scss/cutecasa.scss static/css/bin/cutecasa.css
sass src/scss/cutecasa-splash.scss static/css/bin/cutecasa-splash.css

echo "  Building scripts..."

if  [ ! -d static/js/bin ]
then
    mkdir static/js/bin
fi
tsc

if [ -e "init.sh" ]
then
    echo "  Init script exists."
else
    echo "  Copying init script..."
    cp config/init.sh.example init.sh
    chmod +x init.sh
fi

if [ -e "run.sh" ]
then
    echo "  Run script exists."
else
    echo "  Copying run script..."
    cp config/run.sh.example run.sh
    chmod +x run.sh
fi

echo "-----------------------------------------------------------------------------------"
echo "Build complete - run init.sh to initialize database, or run.sh to start the server."
echo "-----------------------------------------------------------------------------------"
