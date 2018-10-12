from bottle import route, run, request, response
import obf

o=obf.obfuscator()

@route('/encode')
def hello():
    s = request.query.encode
    return o.encode_text(s)

@route('/encode', method='POST')
def helloPOST():
    print(request)
    response.content_type="text/text"
    data = request.files.get('file').file.read()
    s = data.decode("utf-8")
    return o.encode_text(s)



run(host='localhost', port=8080, debug=True)