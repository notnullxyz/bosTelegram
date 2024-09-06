"""
bosServer.py
BosTelegram Python Server 

Old school, most simplistic, chat server for project Veld.
If you need security and privacy, this is not for, unless you know what security-by-obscurity is, then edit the port number :P
See Readme

Author: MarlonV@ProtonMail.com

"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import configparser
import os

# load config - self explanatory
config = configparser.ConfigParser()
config.read('bosTelegram.cfg')
HOST = config['server']['host']
PORT = int(config['server']['port'])
DB_PATH = config['database']['db_path']
ARCHIVE_DAYS = int(config['archive']['archive_days'])
DEBUG_ENABLED = config['debug'].getboolean('enabled')

# init flask
app = Flask(__name__)
CORS(app)  # CORS for all routes

# db path exists?
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# logging debug on or not
if DEBUG_ENABLED:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

# init sqlite db
def init_db():
    logging.debug("Database: init")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        message TEXT NOT NULL,
        datetime TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS archived_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        message TEXT NOT NULL,
        datetime TEXT NOT NULL,
        archive_date TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    logging.debug("Database: init completed")

# archive old chats
def archive_old_chats():
    logging.debug("Archive: Old chats")
    today = datetime.now().date()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE datetime < ?", (today,))
    chats = cursor.fetchall()
    
    for chat in chats:
        cursor.execute('''
        INSERT INTO archived_chats (user, message, datetime, archive_date) 
        VALUES (?, ?, ?, ?)
        ''', (chat[1], chat[2], chat[3], str(today)))
    
    cursor.execute("DELETE FROM chats WHERE datetime < ?", (today,))
    conn.commit()
    conn.close()
    logging.debug("Archive: Old chats: Done")

@app.route('/stash', methods=['GET'])
def stash():
    logging.debug("Stash: Messages older than X - calling archive.");
    archive_old_chats()
    return jsonify({'status': 'OK', 'message': 'Archiving Done'}), 200

# route for sending a single chat message
@app.route('/sendchat', methods=['POST'])
def send_chat():
    logging.debug("/sendchat received")
    data = request.json
    user = data.get('user')
    message = data.get('message')
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO chats (user, message, datetime) 
    VALUES (?, ?, ?)
    ''', (user, message, timestamp))
    conn.commit()
    conn.close()

    logging.debug(f"Chat from user '{user}' with message '{message}' stored in the database.")
    return jsonify({'status': 'success', 'message': 'Chat sent successfully'}), 200

# route to get all messages from today - this isn't optimal so we should do a timed and 'on new' only.
@app.route('/getchats', methods=['GET'])
def get_chats():
    logging.debug("/getchats received")
    # archive_old_chats()
    today = datetime.now().date()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user, message, datetime FROM chats WHERE datetime >= ?", (today,))
    chats = cursor.fetchall()
    conn.close()

    logging.debug(f"/getchats returning {len(chats)} messages.")
    return jsonify([{'user': chat[0], 'message': chat[1], 'datetime': chat[2]} for chat in chats]), 200

# route to get archive all for a specific day
@app.route('/archived', methods=['GET'])
def get_archived_chats():
    logging.debug("Received a request to get archived chats.")
    date = request.args.get('date')
    try:
        archive_date = datetime.strptime(date, '%d/%m/%Y').date()
    except ValueError:
        logging.error("Invalid date format received.")
        return jsonify({'status': 'error', 'message': 'Invalid date format'}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user, message, datetime FROM archived_chats WHERE archive_date = ?", (archive_date,))
    archived_chats = cursor.fetchall()
    conn.close()

    logging.debug(f"Returning {len(archived_chats)} archived chats.")
    return jsonify([{'user': chat[0], 'message': chat[1], 'datetime': chat[2]} for chat in archived_chats]), 200

# route to nuke old archived chats
@app.route('/nuke', methods=['POST'])
def nuke_old_chats():
    logging.debug("Received a request to nuke old archived chats.")
    threshold_date = datetime.now().date() - timedelta(days=ARCHIVE_DAYS)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM archived_chats WHERE archive_date < ?", (threshold_date,))
    conn.commit()
    conn.close()

    logging.debug(f"Nuked chats older than {ARCHIVE_DAYS} days.")
    return jsonify({'status': 'success', 'message': f'Archived chats older than {ARCHIVE_DAYS} days deleted'}), 200

# this is not great, but I needed a test. Anyone can call this and put egg on our faces - clear todays chats.
@app.route('/clearday', methods=['GET'])
def clear_today_chats():
    logging.debug("Received a request to clear today's chats.")
    today = datetime.now().date()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE datetime >= ?", (today,))
    conn.commit()
    conn.close()

    logging.debug("/clearday - today's messages nuked. Anyone can call this, very secure.... great")
    return '', 200  # empty bodied 200 is fine for what I need this for

# dish up a cold chat client on /
@app.route('/')
def index():
    logging.debug("/ call - dish up index/client to user")
    return send_from_directory('static', 'index.htm')

# init, start, go with the flow
if __name__ == '__main__':
    init_db()
    logging.info(f"SERVER STARTED on {HOST}:{PORT} --- DEBUG SET: {DEBUG_ENABLED}")
    app.run(host=HOST, port=PORT, debug=DEBUG_ENABLED)
