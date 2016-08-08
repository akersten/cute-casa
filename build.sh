#!/bin/sh

# Build script to get cutecasa ready. The build script should be non-destructive (in contrast with the init script).

clear

echo "CuteCasa build started..."

echo "  Building stylesheets..."
sass deps/bulma/bulma.sass static/css/bin/bulma.css
sass static/sass/cutecasa.sass static/css/bin/cutecasa.css
sass static/sass/cutecasa-splash.sass static/css/bin/cutecasa-splash.css

if [ -e "init.sh" ]
then
    echo "  Init script exists."
else
    echo "  Copying init script..."
    cp init.sh.example init.sh
fi

if [ -e "run.sh" ]
then
    echo "  Run script exists."
else
    echo "  Copying run script..."
    cp run.sh.example run.sh
fi

echo "-----------------------------------------------------------------------------------"
echo "Build complete - run init.sh to initialize database, or run.sh to start the server."
echo "-----------------------------------------------------------------------------------"
