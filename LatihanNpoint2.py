import requests
from flask import Flask, request

app=Flask(__name__)
@app.route('/cat-and-mouse/x/<inputx>',methods=['GET'])

def catAndMouse(inputx):
    z = request.headers.get('z')
    # a = requests.get('http://localhost:5000')
    x=inputx
    y=request.args.get("y")

    
    if abs(int(z)-int(x))>abs(int(z)-int(y)):
        return{"Hasil:":"Cat B"}
    elif abs(int(z)-int(x))<abs(int(z)-int(y)):
        return{"Hasil:":"Cat A"}
    else:
        return{"Hasil:":"Mouse C"}