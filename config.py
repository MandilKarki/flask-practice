import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10


class ProdConfig(Config):
    SECRET_KEY = '\xcb\xd7\x8a.\x82\x9c1Lu\xf1&2\xf6i\xfa\x8e\xb1\xc9t^\xccW\xdbw'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'Blogs.db')


class DevConfig(Config):
    DEBUG = True
    SECRET_KEY = '\xa8\xcc\xeaP+\xb3\xe8 |\xad\xdb\xea\xd0\xd4\xe8\xac\xee\xfaW\x072@O3'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'Blogs.db')
