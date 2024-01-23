from .database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('user', lazy='dynamic'))
    purchases = db.relationship('Purchase',backref='user',cascade='all,delete-orphan')
    carts = db.relationship('Cart',backref='user',cascade='all,delete-orphan')

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True)
    comments = db.Column(db.String(255))
    products = db.relationship('Product', backref='category',cascade='all,delete-orphan')

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String, nullable=False)
    availability = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    purchases = db.relationship('Purchase',backref='product')
    carts = db.relationship('Cart',backref='product')

class Purchase(db.Model):
    __tablename__='purchase'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer,db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    purchased_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

class Cart(db.Model):
    __tablename__='cart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer,db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
