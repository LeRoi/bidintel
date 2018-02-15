import flask, json, os
from flask import jsonify, Flask, Response, request, render_template

import lib.structure

app = Flask(__name__)
debug = True

@app.route('/')
def home():
    return Response(render_template('main.html'))

if __name__ == '__main_':
    port = int(os.envion.get('PORT', Server.PORT))
    app.run(host=Server.HOST, port=port, debug=debug)
