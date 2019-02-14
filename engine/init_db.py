from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import sqlite3


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
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
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


def setup_roles(cursor, df):
    try:
        # print(list(df))
        for char in df.iterrows():
            _, data = char
            data = list(data[0:2])
            sqlcmd =  """INSERT INTO roles (role_full_name, role_short_name)
                    VALUES
                    ( ?, ?);"""
            cursor.execute(sqlcmd, data)
    except sqlite3.IntegrityError:
        print('Exiting Role function')
        return
    print("Successfully added roles to db")


def setup_actors(cursor, df):
    try:
        # print(list(df))
        for char in df.iterrows():
            _, data = char
            data = list(data[0:2])
            sqlcmd =  """INSERT INTO actors (actor_full_name, actor_initials)
                    VALUES
                    ( ?, ?);"""
            cursor.execute(sqlcmd, data)
    except sqlite3.IntegrityError:
        print('Exiting Actor function')
        return
    print("Successfully added actors to db")


def setup_restaurants(cursor, df):
    try:
        # print(list(df))
        for char in df.iterrows():
            _, data = char
            data = list(data[0:3])
            sqlcmd = """INSERT INTO restaurants (restaurant_full_name, restaurant_short_name, restaurant_seating)
                    VALUES
                    ( ?, ?, ?);"""
            cursor.execute(sqlcmd, data)
    except sqlite3.IntegrityError:
        print('Exiting Restaurant function')
        return
    print("Successfully added restaurants to db")

def setup_scenes(cursor, df):
    try:
        # print(list(df))
        for char in df.iterrows():
            _, data = char
            data = list(data[0:2])
            sqlcmd =  """INSERT INTO scenes (scene_full_name, scene_short_name)
                    VALUES
                    ( ?, ?);"""
            cursor.execute(sqlcmd, data)
    except sqlite3.IntegrityError :
        print('Exiting Scene function')
        return
    print("Successfully added scenes to db")


def setup_ar(cursor, df):
    for _, row in df.iterrows():
        try:
            row = list(row)
            row2 = [x for x in list(df) if row[list(df).index(x)] == 1]
            for i in row2:
                a = [None, None]
                initials = row[1]
                sqlcmd = """INSERT INTO actor_roles (actor_id, role_id)
                values (?, ?);"""
                sqlfetch = """select id from actors where actor_initials = ?"""
                cursor.execute(sqlfetch, [initials])
                a[0] = list(c.fetchone())[0]

                sqlfetch = """select id from roles where role_short_name = ?"""
                cursor.execute(sqlfetch, [i])
                a[1] = list(c.fetchone())[0]
                c.execute(sqlcmd,a)
        except sqlite3.IntegrityError:
            print('Exiting actor_roles function')
            return
        print("Successfully added actor_roles interactions to db")

def setup_srr(cursor, df):
    for _, row in df.iterrows():
        try:
            row = list(row)
            row2 = [x for x in list(df) if row[list(df).index(x)] == 1]
            for i in row2:
                a = [None, None]
                b = [None, None]
                initials = row[1]
                sqlcmd = """INSERT INTO restaurants_scenes (scene_id, restaurant_id)
                values (?, ?);"""
                sqlcmd2 = """INSERT INTO roles_scenes (scene_id, role_id)
                values (?, ?);"""
                sqlfetch = """select id from scenes where scene_short_name = ?"""
                cursor.execute(sqlfetch, [initials])
                a[0] = list(c.fetchone())[0]
                b[0] = a[0]
                try:
                    sqlfetch = """select id from restaurants where restaurant_short_name = ?"""
                    cursor.execute(sqlfetch, [i])
                    a[1] = list(c.fetchone())[0]
                    cursor.execute(sqlcmd,a)
                    # conn.commit()
                except:
                    try:
                        sqlfetch = """select id from roles where role_short_name = ?"""
                        cursor.execute(sqlfetch, [i])
                        b[1] = list(c.fetchone())[0]
                        cursor.execute(sqlcmd2, b)
                        # conn.commit()
                    except:
                        continue
        except sqlite3.IntegrityError:
            continue  


# Create / overwrite Database
if __name__ == '__main__':
    db.create_all()
    filepath = os.path.join(basedir, "assets/data/KORSBAEK_EXCELTEMPLATE_v2.xlsx")
    
    excel = pd.read_excel(filepath, sheet_name=['Actors', 'Characters', 'Restaurants', 'Scenes'])
    actor_df = excel['Actors']
    character_df = excel['Characters']
    restaurant_df = excel['Restaurants']
    scene_df = excel['Scenes']

    print('Connecting to database..')
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    print('Success!')
    
    
    """Add data to DB""" 
    c.execute("""BEGIN TRANSACTION""")
    setup_roles(c, character_df)
    setup_actors(c, actor_df)
    setup_restaurants(c, restaurant_df)
    setup_scenes(c, scene_df)
    setup_srr(c, scene_df)
    setup_ar(c, actor_df)
    c.execute("""COMMIT TRANSACTION""")
    conn.commit()
    print('Done')


    print('Closing Connection')
    conn.close()




    

    
    