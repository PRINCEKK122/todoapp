from flask import Flask, render_template, request, redirect, url_for
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

    def __repr__(self):
        return f"<Todo {self.id} {self.description}>"


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template(
        "index.html",
        data=Todo.query.all(),
    )


@app.route("/todos/create", methods=["POST"])
def create_todo():
    new_todo = request.form.get("description", None)

    try:
        todo = Todo(description=new_todo) # transient mode
        # creating a session, which is the same as a transaction
        db.session.add(todo)
        # now we are ready to flush the newly created data
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for("index"))
