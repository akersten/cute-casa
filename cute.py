# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

import os

# Read configuration from environment variables - these are set by the secret script that we don't commit...
DATABASE = os.environ.get('CUTE_DB')
DEBUG = os.environ.get('CUTE_DEBUG') in ['True', 'true', '1', 'yes']
SECRET_KEY = os.environ.get('CUTE_SECRET_KEY')
USERNAME = os.environ.get('CUTE_USERNAME')
PASSWORD = os.environ.get('CUTE_PASSWORD')

if USERNAME is None:
    print("Username not set! Run through the secret shell script.")
    exit(1)

if PASSWORD is None:
    print("Password not set! Run through the secret shell script.");
    exit(1)

if SECRET_KEY is None:
    print("Secret key not set! Run through the secret shell script.");
    exit(1)

print("k")



