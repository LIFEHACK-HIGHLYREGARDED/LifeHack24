from flask import Flask, request
from backendapi import insertIntoDB, queryDB
app = Flask(__name__)

@app.route('/')
def hello():
	return "Hello World!"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)


@app.route('/insert', methods=["POST"])
def insert():
	url = request.form['url']
	insertIntoDB(url)
	return "Success"

@app.route("query", methods=["POST"])
def query():
	qry = request.form['query']
	result = queryDB(qry)
	return result