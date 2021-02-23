import typing

from flask import Flask
app : Flask = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello_world() -> str:
    return """
    <pre>/index</pre> page
    """

if __name__ == '__main__':
    app.run(debug=True)