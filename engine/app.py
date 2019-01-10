from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# init app

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)

actors_roles = db.Table('actor_roles',
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

restaurants_scenes = db.Table('restaurants_scenes',
    db.Column('restaurants_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
    db.Column('scene_id', db.Integer, db.ForeignKey('scenes.id'), primary_key=True)
)

roles_scenes = db.Table('roles_scenes',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('scene_id', db.Integer, db.ForeignKey('scenes.id'), primary_key=True)
)


class Actors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_full_name = db.Column(db.String(), unique=True)
    actor_initials = db.Column(db.String(3))
    roles = db.relationship('Role', secondary=actors_roles, lazy='subquery',
    backref=db.backref('roles', lazy=True))

    
class Scenes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scene_full_name = db.Column(db.String(), unique=True)
    scene_short_name = db.Column(db.String(20), unique=True)
    restaurants = db.relationship('Restaurants', secondary=restaurants_scenes, lazy='subquery',
    backref=db.backref('restaurants', lazy=True))
    roles = db.relationship('Roles', secondary=roles_scenes, lazy='subquery',
    backref=db.backref('roles', lazy=True))


class Restaurants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_full_name = db.Column(db.String(), unique=True)
    restaurant_short_name = db.Column(db.String(20), unique=True)
    restaurant_seating = db.Column(db.Integer)


class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_full_name = db.Column(db.String(), unique=True)
    role_short_name = db.Column(db.String(), unique=True)


# Create / overwrite Database
if __name__ == '__main__':
    db.create_all()
