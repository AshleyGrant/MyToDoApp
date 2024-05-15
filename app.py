from flask import Flask, render_template, request, redirect, url_for, g
from database import db, Todo
from recommendation_engine import RecommendationEngine
import json
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "todos.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.before_request
def load_data_to_g():
    todos = Todo.query.all()
    g.todos = todos
    g.todo = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_todo():
    # get the data from the form
    todo = Todo(
        name=request.form["todo"],
    )

    # add the new ToDo to the list
    db.session.add(todo)
    db.session.commit()
    
    # add the new ToDo to the list
    return redirect(url_for("index"))

@app.route("/remove/<int:id>", methods=["GET", "POST"])
def remove_todo(id):
    db.session.delete(Todo.query.filter_by(id=id).first())
    db.session.commit()
    return redirect(url_for("index"))

# Show AI recommendations
@app.route('/recommend/<int:id>', methods=['GET'])
async def recommend(id):
    recommendation_engine = RecommendationEngine()
    g.todo = db.session.query(Todo).filter_by(id=id).first()

    if g.todo:
        try:
            #attempt to load any saved recommendation from the DB
            if g.todo.recommendations_json is not None:
                g.todo.recommendations = json.loads(g.todo.recommendations_json)
                return render_template('index.html')
        except ValueError as e:
            print("Error:", e)

    g.todo.recommendations = await recommendation_engine.get_recommendations(g.todo.name)
        
    # Save the recommendations to the database
    try:
        g.todo.recommendations_json = json.dumps(g.todo.recommendations)
        db.session.add(g.todo)
        db.session.commit()
    except Exception as e:
        print(f"Error adding and committing todo: {e}")
        return

    return render_template('index.html')

if __name__ == "__main__":
    recommendations = []   
    app.run(debug=True)