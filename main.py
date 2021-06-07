from flask import Flask
from flask import request, escape

app = Flask(__name__)

@app.route("/")
def index():
    answer = str(escape(request.args.get("answer", "")))
    task = """Дано: print(something, type(something)). <br> Сравните типы объектов."""
    return (task + 
            
        """<form action="" method="get">
                <input type="text" name="code">
                <input type="submit" value="Ответить">
              </form>"""
            )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)