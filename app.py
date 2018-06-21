from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost/users_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'ihaveasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

modus = Modus(app)
db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    messages = db.relationship("Message", backref="user")
    image = db.Column(db.Text)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    msg_content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


msgs_tags = db.Table(
    "msgs_tags", db.Column('id', db.Integer, primary_key=True),
    db.Column('message_id', db.Integer, db.ForeignKey('messages.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')))


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.Text)
    messages = db.relationship(
        "Message", secondary="msgs_tags", backref="tags")


db.create_all()

# User Routes


@app.route('/users', methods=['GET'])
def user_index():
    users = User.query.all()
    return render_template('user_index.html', users=users)


@app.route('/users/new', methods=['GET'])
def user_new():
    return render_template('user_new.html')


@app.route('/users', methods=['POST'])
def user_create():
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image=request.form['image'])
    print(new_user)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('user_index'))


@app.route('/users/<int:user_id>', methods=['GET'])
def user_show(user_id):
    found_user = User.query.get(user_id)
    return render_template('user_show.html', user=found_user)


@app.route('/users/<int:user_id>', methods=['DELETE'])
def user_delete(user_id):
    found_user = User.query.get(user_id)
    db.session.delete(found_user)
    db.session.commit()
    return redirect(url_for('user_index'))


@app.route('/users/<int:user_id>/edit', methods=['GET'])
def user_edit_form(user_id):
    """Show the edit user form."""
    found_user = User.query.get(user_id)
    return render_template('user_edit.html', user=found_user)


@app.route('/users/<int:user_id>', methods=['PATCH'])
def user_edit(user_id):
    found_user = User.query.get(user_id)
    found_user.first_name = request.form['first_name']
    found_user.last_name = request.form['last_name']
    found_user.image = request.form['image']
    db.session.add(found_user)
    db.session.commit()
    return redirect(url_for('user_show', user_id=found_user.id))


# Messages Routes


@app.route('/users/<int:user_id>/messages')
def index_messages(user_id):
    user = User.query.get(user_id)
    return render_template("msg_index.html", user=user)


@app.route('/users/<int:user_id>/newmsg')
def msg_new(user_id):
    user = User.query.get(user_id)
    return render_template('msg_new.html', user=user)


@app.route('/users/<int:user_id>/messages', methods=['POST'])
def msg_create(user_id):
    new_msg = Message(msg_content=request.form['msg_content'], user_id=user_id)
    db.session.add(new_msg)
    db.session.commit()
    return redirect(url_for('index_messages', user_id=user_id))


@app.route('/messages/<int:msg_id>', methods=['DELETE'])
def msg_delete(msg_id):
    found_msg = Message.query.get(msg_id)
    db.session.delete(found_msg)
    db.session.commit()
    return redirect(url_for('index_messages', user_id=found_msg.user_id))


@app.route('/messages/<int:msg_id>/edit', methods=['GET'])
def msg_edit_form(msg_id):
    found_msg = Message.query.get(msg_id)
    return render_template('msg_edit.html', found_msg=found_msg)


@app.route('/messages/<int:msg_id>', methods=['PATCH'])
def msg_edit(msg_id):
    found_msg = Message.query.get(msg_id)
    found_msg.msg_content = request.form['msg_content']
    db.session.add(found_msg)
    db.session.commit()
    return redirect(url_for('index_messages', user_id=found_msg.user_id))


# Tag Routes


@app.route('/tags', methods=['GET'])
def tag_index():
    tags = Tag.query.all()
    return render_template('tags_index.html', tags=tags)


@app.route('/tags/new', methods=['GET'])
def tag_new_form():
    return render_template('tags_new.html')


@app.route('/tags/new', methods=['POST'])
def tag_create():
    new_tag = Tag(tag_name=request.form['tag_name'])
    db.session.add(new_tag)
    db.session.commit()
    return redirect(url_for('tag_index'))
