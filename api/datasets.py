from flask import app, send_file


def dashboard():
    return send_file("out-min/dashboard.json")


def wall_of_shame():
    return send_file("out-min/wall-of-shame.json")
