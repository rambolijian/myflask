from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/static/<filename>")
@app.route("/")
def index():
    return '<h1>Hello World！</h1>'

if __name__ == "__main__":
    app.run(debug=True)