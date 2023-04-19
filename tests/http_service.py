#!/usr/bin python3
# @File    : http_service.py
# @Time    : 2020/2/15 15:05
# @Author  : Kelvin.Ye
from flask import Flask
from flask import make_response
from flask import request


app = Flask(__name__)


@app.route('/get', methods=['GET'])
def get():
    response = make_response(request.args, 200)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response


@app.route('/post', methods=['POST'])
def post():
    response = make_response(request.json, 200)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response


if __name__ == '__main__':
    app.run(debug=True)
