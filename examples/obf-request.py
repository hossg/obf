import requests
files = {'file': open('plaintext.txt', 'rb')}
r = requests.post('http://localhost:8080/encode',files=files)
print(r.text)
