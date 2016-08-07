#!/bin/sh

# Build script to get cutecasa ready. The build script should be non-destructive (in contrast with the init script).

echo "Building stylesheets..."
sass deps/bulma/bulma.sass static/css/bin/bulma.css
sass static/sass/cutecasa.sass static/css/bin/cutecasa.css
sass static/sass/cutecasa-splash.sass static/css/bin/cutecasa-splash.css

echo "Done!"
