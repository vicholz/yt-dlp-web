#!/usr/bin/env python3

import os
import datetime
import json
import logging
from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask import request
from yt_dlp import YoutubeDL


DEFAULT_OUTPUT_PATH = "/tmp/yt-dlp-web"
DEFAULT_STATIC_PATH = "web/static"
DEFAULT_TEMPLATE_PATH = "web/template"

DEFAULT_YT_DLP_CONFIG = {
    "paths": { 
        "home": DEFAULT_OUTPUT_PATH,
    },
    "postprocessors": [
        {
            'key': 'FFmpegMetadata',
            'add_metadata': True,
            'add_chapters': True,
            "add_infojson": True,
        },
        {
            "key": "FFmpegEmbedSubtitle",
            "already_have_subtitle": True
        },
        {
            "key": "EmbedThumbnail",
            "already_have_thumbnail": True
        }
    ],
    "subtitleslangs": ["en"],
    "embedsubtitles": True,
    "embedthumbnail": True,
    "embed_infojson": True,
    "addchapters": True,
    "addmetadata": True,
    "continuedl": True,
    "verbose": True
}

if not os.path.exists(DEFAULT_OUTPUT_PATH): os.mkdir(DEFAULT_OUTPUT_PATH)

app = Flask(__name__,
            static_url_path='', 
            static_folder=DEFAULT_STATIC_PATH,
            template_folder=DEFAULT_TEMPLATE_PATH
            )

def load_config(file: str = "config.json") -> dict:
    if not os.path.isfile(file):
        error = "Could not load config file '{file}'. Please check and try again!"
        logging.error(error)
        return DEFAULT_YT_DLP_CONFIG
    else:
        with open(file, "r") as f:
            config = json.load(f)
            f.close()
            return config

def download_video(url: str):
    config = load_config()
    with YoutubeDL(config) as ydl:
        return_code = ydl.download([url])
    return return_code

@app.route('/')
def root():
    files = get_files()
    return render_template(os.path.join("index.html"), files=files)

@app.route('/download')
def download():
    url = request.args.get('url')
    result = download_video(url)
    if result == 0:
        return {"status": "success"}
    else:
        return {"status": "failed"}
    
@app.route('/get-files')
def get_files():
    files = os.listdir(DEFAULT_OUTPUT_PATH)
    rtn = []
    for file in files:
        abs_file = os.path.join(DEFAULT_OUTPUT_PATH, file)
        if os.path.isfile(abs_file):
            f = {
                    "name": file,
                    "url": f"/get-file?file={file}",
                    "size": os.path.getsize(abs_file),
                    "date_created": datetime.datetime.fromtimestamp(os.path.getctime(abs_file))
                }
            rtn.append(f)
    return rtn

@app.route('/get-file')
def get_file():
    file = request.args.get('file')
    file = file.replace("../","")
    if file:
        abs_file = os.path.join(DEFAULT_OUTPUT_PATH, file)
        if os.path.isfile(abs_file):
            return send_from_directory(DEFAULT_OUTPUT_PATH, file)
        else:
            return '{"message": "FAILED"}'
    return '{"message": "FAILED"}'

@app.route('/delete-file')
def delete_file():
    file = request.args.get('file')
    file = file.replace("../","")
    if file:
        abs_file = os.path.join(DEFAULT_OUTPUT_PATH, file)
        if os.path.isfile(abs_file):
            os.remove(abs_file)
            return '{"message": "OK"}'
        else:
            return '{"message": "FAILED"}'
    return '{"message": "FAILED"}'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(
            app.root_path,
            DEFAULT_STATIC_PATH
        ),
        'favicon.ico'
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
