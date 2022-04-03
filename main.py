import datetime

from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from config import DevConfig
from flask_migrate import Migrate
from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from sqlalchemy import func, desc

from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)
Base = declarative_base()
migrate = Migrate(app, db)

#
# @app.route('/')
# def home():
#     return '<h1> Hello World </h1>'


tags = Table(
    'post_tags', Base.metadata,
    Column('post_id', Integer(), ForeignKey('post.id')),
    Column('tag_id', Integer(), ForeignKey('tag.id'))
)


class User(db.Model):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))

    posts = relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class Post(db.Model):
    __tablename__ = "Post"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    text = Column(Text())
    publish_date = Column(DateTime(), default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey('user.id'))
    comments = relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    tags = relationship(
        'Tag',
        secondary=tags,
        backref=backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)


class Comment(db.Model):
    __tablename__ = "Comment"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    text = Column(Text(), nullable=False)
    date = Column(DateTime(), default=datetime.datetime.now)
    post_id = Column(Integer, ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Tag(db.Model):
    __tablename__ = "Tag"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)


class CommentForm(Form):
    __tablename__ = "CommentForm"
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=255)]
    )
    text = TextAreaField(u'Comment', validators=[DataRequired()])


def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
    ).join(tags).group_by(Tag).order_by(desc('total')).limit(5).all()

    return recent, top_tags

#
# @app.route('/')
# def home():
#     result = "<h1>Tables</h1><br><ul>"
#     for table in db.metadata.tables.items():
#         result += "<li>%s</li>" % str(table)
#     result += "</ul>"
#     return result


@app.route('/')
@app.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, app.config.get('POSTS_PER_PAGE', 10), False)
    recent, top_tags = sidebar_data()

    return render_template(
        'home.html',
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@app.route('/post/<int:post_id>', methods=('GET', 'POST'))
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        try:
            db.session.add(new_comment)
            db.session.commit()
        except Exception as e:
            flash('Error adding your comment: %s' % str(e), 'error')
            db.session.rollback()
        else:
            flash('Comment added', 'info')
        return redirect(url_for('post', post_id=post_id))

    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'post.html',
        post=post,
        tags=tags,
        comments=comments,
        recent=recent,
        top_tags=top_tags,
        form=form
    )


@app.route('/posts_by_tag/<string:tag_name>')
def posts_by_tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'tag.html',
        tag=tag,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@app.route('/posts_by_user/<string:username>')
def posts_by_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')








