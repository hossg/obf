#! python3

from bottle import route, run, request, response, static_file

# A super simple dummy web service that will retrieve a resource and return it to the caller.
# Used only to allow demonstration of the obf proxy service

@route('/retrieve/<file:path>')
def server_static(file):
    return static_file(file,root='.')

run(host='localhost', port=8080, debug=True)