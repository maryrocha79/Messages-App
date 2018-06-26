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
    image = db.Column(db.Text)
    messages = db.relationship(
        "Message", backref="user", lazy="dynamic", cascade="all,delete")


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


msgs_tags_table = db.Table(
    "msgs_tags",
    db.Column('message_id', db.Integer, db.ForeignKey('messages.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')))


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    messages = db.relationship(
        'Message',
        lazy="dynamic",
        secondary=msgs_tags_table,
        cascade="all,delete",
        backref=db.backref('tags', lazy="dynamic"))


db.create_all()

# User Routes


@app.route('/users', methods=['GET'])
def user_index():
    """Renders the page with all users."""
    users = User.query.all()
    return render_template('user_index.html', users=users)


@app.route('/users/new', methods=['GET'])
def user_new():
    """Shows the form to add a user."""
    return render_template('user_new.html')


@app.route('/users', methods=['POST'])
def user_create():
    """Creates a new user."""
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image=request.form['image'])
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('user_index'))


@app.route('/users/<int:user_id>', methods=['GET'])
def user_show(user_id):
    """Shows the profile of a user."""
    found_user = User.query.get_or_404(user_id)
    return render_template('user_show.html', user=found_user)


@app.route('/users/<int:user_id>', methods=['DELETE'])
def user_delete(user_id):
    """Deletes an user."""
    found_user = User.query.get(user_id)
    db.session.delete(found_user)
    db.session.commit()
    return redirect(url_for('user_index'))


@app.route('/users/<int:user_id>/edit', methods=['GET'])
def user_edit_form(user_id):
    """Show the edit user form."""
    found_user = User.query.get_or_404(user_id)
    return render_template('user_edit.html', user=found_user)


@app.route('/users/<int:user_id>', methods=['PATCH'])
def user_edit(user_id):
    """Updates an user"""
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
    """Shows all messages of an user."""
    user = User.query.get(user_id)
    return render_template("msg_index.html", user=user)


@app.route('/users/<int:user_id>/newmsg')
def msg_new(user_id):
    """Shows the form to add a new message"""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('msg_new.html', user=user, tags=tags)


@app.route('/users/<int:user_id>/messages', methods=['POST'])
def msg_create(user_id):
    """Creates a new message for an user"""
    new_msg = Message(content=request.form['content'], user_id=user_id)

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    new_msg.tags = Tag.query.filter(Tag.id.in_(tag_ids))

    db.session.add(new_msg)
    db.session.commit()
    return redirect(url_for('index_messages', user_id=user_id))


@app.route('/messages/<int:msg_id>', methods=['GET'])
def msg_show(msg_id):
    """Shows one messages and its tags"""
    found_msg = Message.query.get_or_404(msg_id)
    return render_template('msg_show.html', found_msg=found_msg)


@app.route('/messages/<int:msg_id>', methods=['DELETE'])
def msg_delete(msg_id):
    """Deletes a message from an user"""
    found_msg = Message.query.get_or_404(msg_id)
    user = found_msg.user
    db.session.delete(found_msg)
    db.session.commit()
    return redirect(url_for('index_messages', user_id=user.id))


@app.route('/messages/<int:msg_id>/edit', methods=['GET'])
def msg_edit_form(msg_id):
    """Shows the form to edit a message"""
    found_msg = Message.query.get(msg_id)
    tags = Tag.query.all()
    return render_template('msg_edit.html', found_msg=found_msg, tags=tags)


@app.route('/messages/<int:msg_id>', methods=['PATCH'])
def msg_edit(msg_id):
    """Edits the message of a user"""
    found_msg = Message.query.get_or_404(msg_id)
    found_msg.content = request.form['content']
    tag_ids = [int(num) for num in request.form.getlist('tags')]
    found_msg.tags = Tag.query.filter(Tag.id.in_(tag_ids))
    user = found_msg.user
    db.session.add(found_msg)
    db.session.commit()
    return redirect(url_for('index_messages', user_id=user.id))


# Tag Routes


@app.route('/tags', methods=['GET'])
def tag_index():
    """Shows the list of tags"""
    tags = Tag.query.all()
    return render_template('tags_index.html', tags=tags)


@app.route('/tags/new', methods=['GET'])
def tag_new_form():
    """ Shows the form to add a new tag"""
    messages = Message.query.all()
    return render_template('tags_new.html', messages=messages)


@app.route('/tags/new', methods=['POST'])
def tag_create():
    """ Handle adding a new tag"""
    new_tag = Tag(name=request.form['name'])
    message_ids = [int(num) for num in request.form.getlist('messages')]
    new_tag.messages = Message.query.filter(Message.id.in_(message_ids))
    db.session.add(new_tag)
    db.session.commit()
    return redirect(url_for('tag_index'))


@app.route('/tags/<int:tag_id>', methods=['GET'])
def tag_show(tag_id):
    """Shows one tag and the messages associated with it """
    found_tag = Tag.query.get_or_404(tag_id)
    return render_template('tags_show.html', found_tag=found_tag)


@app.route('/tags/<int:tag_id>', methods=['DELETE'])
def tag_delete(tag_id):
    """Handle deleting one tag"""
    found_tag = Tag.query.get(tag_id)
    db.session.delete(found_tag)
    db.session.commit()
    return redirect(url_for('tag_index'))


@app.route('/tags/<int:tag_id>/edit', methods=['GET'])
def tag_edit_form(tag_id):
    """Shows the for to add a new tag"""
    found_tag = Tag.query.get_or_404(tag_id)
    messages = Message.query.all()
    return render_template(
        'tags_edit.html', found_tag=found_tag, messages=messages)


@app.route('/tags/<int:tag_id>', methods=['PATCH'])
def tag_edit(tag_id):
    """Handle editing one tag"""
    found_tag = Tag.query.get_or_404(tag_id)
    found_tag.name = request.form['name']
    message_ids = [int(num) for num in request.form.getlist('messages')]
    found_tag.messages = Message.query.filter(Message.id.in_(message_ids))
    db.session.add(found_tag)
    db.session.commit()
    return redirect(url_for('tag_index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
