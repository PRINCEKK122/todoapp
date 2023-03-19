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

    def __repr__(self):
        return f"<Todo {self.id} {self.description}>"


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template(
        "index.html",
        data=Todo.query.order_by(Todo.id).all(),
    )


@app.route("/todos/create", methods=["POST"])
def create_todo():
    body = {}
    error = False
    try:
        description = request.get_json()["description"]
        todo = Todo(description=description)
        body["description"] = todo.description
        db.session.add(todo)
        db.session.commit()
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


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
