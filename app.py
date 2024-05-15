from flask import Flask, render_template, request, redirect, url_for
import os

todo_list = []

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
todo_file = os.path.join(basedir, "todo_list.txt")

try:
    with open(todo_file, "r") as file:
        for line in file:
            todo_list.append(line.strip())
except FileNotFoundError:
    print("No saved items found")

@app.route("/")
def index():
    return render_template("index.html", todo_list=todo_list)

if __name__ == "__main__":
    app.run(debug=True)