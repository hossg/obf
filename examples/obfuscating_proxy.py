#! python3

# A simple Flask-based reverse proxy to act as a MITM-style proxy, obfuscating responses from an upstream server
# Implementation taken from: https://medium.com/customorchestrator/simple-reverse-proxy-server-using-flask-936087ce0afb

from flask import Flask,request,redirect,Response
import requests
import obf
import json

app = Flask(__name__)
SITE_NAME = 'http://localhost:8080/'
o=obf.obfuscator()
keys_to_encode=['color','category']

@app.route('/')
def index():
    return 'Flask is running!'

@app.route('/<path:path>',methods=['GET'])
def proxy(path):
    if request.method=='GET':
        resp = requests.get(f'{SITE_NAME}{path}')
        app.logger.info(resp.headers)
        content_s=resp.content.decode('UTF-8')
        if resp.headers['Content-Type'].startswith("text/plain"):
            content=o.encode_text(content_s)
        elif resp.headers['Content-Type'].startswith("application/json"):
            content=json.dumps(o.encode_json(resp.content,selected_keys=keys_to_encode))
            app.logger.info(resp.content)
            app.logger.info(content)
        else:
            content=resp.content
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in     resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(content, resp.status_code, headers)
    return response


if __name__ == '__main__':
    app.run(debug=True, port=8081)