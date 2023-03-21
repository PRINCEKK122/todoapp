import sys

from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:abc@localhost:5432/todoapp"
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    todolists = db.Column(db.Integer, db.ForeignKey("todolists.id"), nullable=False)

    def __repr__(self):
        return f"<Todo {self.id} {self.description}>"


class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    todos = db.relationship("Todo", backref="list", lazy=True)

    def __repr__(self):
        return f"<TodoList {self.id} {self.name}>"


with app.app_context():
    db.create_all()


##################################################
###### TODOITEMS ROUTES
##################################################
@app.route("/")
def index():
    return redirect(url_for("get_list_todos", list_id=1))


@app.route("/lists/<int:list_id>")
def get_list_todos(list_id):
    return render_template(
        "index.html",
        lists=TodoList.query.all(),
        active_list=TodoList.query.get(list_id),
        data=Todo.query.filter_by(todolists=list_id).order_by(Todo.id).all(),
    )


@app.route("/todos/create", methods=["POST"])
def create_todo():
    body = {}
    error = False
    try:
        description = request.get_json()["description"]
        list_id = request.get_json()["list_id"]
        todo = Todo(description=description)
        active_list = TodoList.query.get(list_id)
        todo.list = active_list
        db.session.add(todo)
        db.session.commit()
        body["description"] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(body)


@app.route("/todos/<int:todo_id>/set-completed", methods=["POST"])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()["completed"]
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        print("Failed to set complete")
    finally:
        db.session.close()
    return jsonify({"success": True})


@app.route("/todos/<int:todo_id>/delete_todo", methods=["DELETE"])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        print(todo)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return jsonify({"success": True})


#######################################################
######## TODOITEMS ROUTES
#######################################################
@app.route("/todoitems", methods=["POST"])
def create_todoitems():
    body = {}
    error = False
    try:
        name = request.get_json()["name"]
        print(name)
        todolist = TodoList(name=name)
        print(todolist)
        db.session.add(todolist)
        db.session.commit()
        body["name"] = name
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        print("Something went wrong")
        abort(400)
    else:
        return jsonify(body)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
