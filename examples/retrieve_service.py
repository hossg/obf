#! python3

# A simple Flask-based service to retrieve a file, to simulate a web-service

from flask import Flask, send_file

app = Flask(__name__)
keys_to_encode=['color','category']

@app.route('/')
def index():
    return 'Flask is running!'

@app.route('/retrieve/<path:path>',methods=['GET'])
def proxy(path):
    return send_file(f'{path}')

if __name__ == '__main__':
    app.run(debug=True, port=8080)