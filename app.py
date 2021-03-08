from sort import app
from config import host

if __name__ == "__main__":
    app.run(host=host, port=5000, debug=True)
