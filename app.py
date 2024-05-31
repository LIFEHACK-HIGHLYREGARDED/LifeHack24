from flask import Flask, request
from backendapi import insertIntoDB, queryDB
app = Flask(__name__)

@app.route('/')
def hello():
	return "Hello World!"

@app.route('/insert', methods=["POST"])
def insert():
	if not request.form or 'url' not in request.form:
		return "Missing URL parameter", 400

	url = request.form['url']
	insertIntoDB(url)
	return "Success", 200

@app.route("/query", methods=["POST"])
def query():
	if not request.form or 'query' not in request.form:
		return "Missing URL parameter", 400
	qry = request.form['query']
	result = queryDB(qry)
	return result, 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)