#!/bin/sh

# Run less to build the CSS files for cutecasa.
lessc static/less/cutecasa.less > static/css/cutecasa.css
lessc static/less/splash.less > static/css/splash.css
