from flask_restful import Resource, fields, marshal, reqparse
from flask_security import current_user, auth_required, roles_required, roles_accepted, hash_password
from application.models import *
from .database import db
import string, random
from datetime import datetime

cart_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'product_id': fields.Integer,
    'quantity': fields.Integer
}

cart_parser = reqparse.RequestParser()
cart_parser.add_argument('user_id')
cart_parser.add_argument('product_id')
cart_parser.add_argument('quantity')

purchase_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'product_id': fields.Integer,
    'quantity': fields.Integer,
    'purchased_at': fields.DateTime
}

purchase_parser = reqparse.RequestParser()
purchase_parser.add_argument('user_id')
purchase_parser.add_argument('product_id')
purchase_parser.add_argument('quantity')
purchase_parser.add_argument('purchased_at')

product_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'expiry': fields.DateTime(dt_format='iso8601'),
    'price': fields.Float,
    'unit': fields.String,
    'availability': fields.Integer,
    'quantity': fields.Integer,
    'category_id': fields.Integer,
    'purchases': fields.Nested(purchase_fields),
    'carts': fields.Nested(cart_fields)
}

product_parser = reqparse.RequestParser()
product_parser.add_argument('name')
product_parser.add_argument('expiry')
product_parser.add_argument('price')
product_parser.add_argument('unit')
product_parser.add_argument('availability')
product_parser.add_argument('category_id')

category_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'active': fields.Boolean,
    'comments': fields.String,
    'products': fields.Nested(product_fields)
}

category_parser = reqparse.RequestParser()
category_parser.add_argument('name')

role_fields = {
    'id': fields.Integer,
    'name': fields.String
}

user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
    'name': fields.String,
    'active': fields.Boolean,
    'roles': fields.Nested(role_fields),
    'purchases': fields.Nested(purchase_fields),
    'carts': fields.Nested(cart_fields)
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('email')
user_parser.add_argument('username')
user_parser.add_argument('name')
user_parser.add_argument('password')
user_parser.add_argument('confirmPassword')
user_parser.add_argument('role')

class UsersAPI(Resource):
    @auth_required('token')
    def get(self):
        role = current_user.roles[0].name
        print(role)
        user = User.query.filter_by(email=current_user.email).first()
        if not user:
            return {"message":"Invalid email"}, 404
        return marshal(user, user_fields), 200
    
    def post(self):
        args = user_parser.parse_args()
        email = args.get('email',None)
        username = args.get('username',None)
        name = args.get('name',None)
        password = args.get('password',None)
        confirmPassword = args.get('confirmPassword',None)
        role = args.get('role',None)
        if role == 'manager':
            active = 0
        else:
            active = 1
        fs_uniquifier = ''.join(random.choices(string.ascii_letters,k=10))
        if any(field is None for field in (email, username, name, password, role)):
            return {"message":"One or more fields are empty"}, 400
        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            return {"message":"Email already exists"},400
        if password != confirmPassword:
            return {"message":"Password does not match"}, 400
        user = User(email=email, username=username, name=name, password=hash_password(password), active=active, fs_uniquifier=fs_uniquifier)
        user_role = Role.query.filter_by(name=role).first()
        user.roles.append(user_role)
        db.session.add(user)
        db.session.commit()
        return marshal(user, user_fields), 201
    
    @roles_required('admin')
    def put(self, id):
        user = User.query.get(id)
        if not user:
            return {"message":"Invalid ID"}, 404
        user.active = 1
        db.session.commit()
        return {"message":"Manager Signup approval done"}, 200
    
class CategoriesAPI(Resource):
    def get(self, id=None):
        if id is None:
            categories = Category.query.filter_by(active=True).all()
            return marshal(categories, category_fields), 200
        category = Category.query.get(id)
        if not category:
            return {"message":"Invalid ID"}, 404
        elif category.active is False:
            return {"message":"Approval pending from admin"}, 404
        else:
            return marshal(category, category_fields), 200

    @roles_accepted('manager','admin')
    def post(self):
        args = category_parser.parse_args()
        name = args.get('name',None)
        if name is None:
            return {"message":"Name is required"}, 400
        category_exist = Category.query.filter_by(name=name).first()
        if category_exist:
            return {"message":"Category already exists"}, 400
        role = current_user.roles[0].name
        if role == 'manager':
            active = 0
            comments = f'{current_user.username} wants to add this category'
            category = Category(name=name, active=active, comments=comments)
            db.session.add(category)
            db.session.commit()
            return {"message":"Add category approval sent successfully to Admin"}, 201
        active = 1
        comments = ''
        category = Category(name=name, active=active, comments=comments)
        db.session.add(category)
        db.session.commit()
        return marshal(category, category_fields), 201
    
    @roles_accepted('manager','admin')
    def delete(self, id):
        category = Category.query.get(id)
        if not category:
            return {"message":"Invalid ID"}, 404
        role = current_user.roles[0].name
        if role == 'manager':
            category.comments = f'{current_user.username} wants to delete this category'
            category.active = 0
            db.session.commit()
            return {"message":"Delete category approval sent successfully to Admin"}, 200
        db.session.delete(category)
        db.session.commit()
        return {"message":"Category deleted successfully"}, 200
    
    @roles_accepted('manager','admin')
    def put(self, id):
        category = Category.query.get(id)
        if not category:
            return {"message":"Invalid ID"}, 404
        args = category_parser.parse_args()
        name = args.get('name',None)    
        if name is None:
            return {"message":"Name is required"}, 400
        category_exist = Category.query.filter_by(name=name).first()
        if category_exist and category_exist.id != category.id:
            return {"message":"Category already exists"}, 400
        role = current_user.roles[0].name
        if role == 'manager':
            category.comments = f'{current_user.username} wants to change the name from {category.name} to {name}'
            category.name = name
            category.active = 0
            db.session.commit()
            return {"message":"Edit category approval sent successfully to Admin"}, 200
        category.comments = ''
        category.name = name
        category.active = 1
        db.session.commit()
        # return marshal(category, category_fields), 200
        return {"message":f"Category {category.name} approved"}, 200
    
class ProductsAPI(Resource):
    def get(self, id=None):
        if id is None:
            products = Product.query.all()
            return marshal(products, product_fields), 200
        product = Product.query.get(id)
        if product:
            return marshal(product, product_fields), 200
        else:
            return {"message":"Invalid ID"}, 404
    
    @roles_required('manager')
    def post(self):
        args = product_parser.parse_args()
        name = args.get('name',None)
        expiry = datetime.strptime(args.get('expiry',None),'%Y-%m-%d')
        # expiry = args.get('expiry',None)
        price = args.get('price',None)
        unit = args.get('unit',None)
        availability = args.get('availability',None)
        category_id = args.get('category_id',None)
        if any(field is None for field in (name, expiry, price, unit, availability, category_id)):
            return {"message":"One or more fields are empty"}, 400
        category = Category.query.get(category_id)
        if not category:
            return {"message":"Category not exists"}, 400
        product_exist = Product.query.filter_by(name=name, category_id=category_id).first()
        if product_exist:
            return {"message":"Product already exists in this category"}, 400
        product = Product(name=name, expiry=expiry, price=price, unit=unit, availability=availability, category_id=category_id)
        db.session.add(product)
        db.session.commit()
        return marshal(product, product_fields), 201
    
    @roles_required('manager')
    def delete(self, id):
        product = Product.query.get(id)
        if not product:
            return {"message":"Invalid ID"}, 404
        db.session.delete(product)
        db.session.commit()
        return {"message":"Product deleted successfully"}, 200
    
    @roles_required('manager')
    def put(self, id):
        product = Product.query.get(id)
        if not product:
            return {"message":"Invalid ID"}, 404
        args = product_parser.parse_args()
        name = args.get('name',None)
        expiry = datetime.strptime(args.get('expiry',None),'%Y-%m-%d')
        price = args.get('price',None)
        unit = args.get('unit',None)
        availability = args.get('availability',None)
        category_id = args.get('category_id',None)
        if any(field is None for field in (name, expiry, price, unit, availability, category_id)):
            return {"message":"One or more fields are empty"}, 400
        category = Category.query.get(category_id)
        if not category:
            return {"message":"Category not exists"}, 400
        product_exist = Product.query.filter_by(name=name, category_id=category_id).first()
        if product_exist and product_exist.id != product.id:
            return {"message":"Product already exists in this category"}, 400
        product.name = name
        product.expiry = expiry
        product.price = price
        product.unit = unit
        product.availability = availability
        product.category_id = category_id
        db.session.commit()
        return marshal(product, product_fields), 200        
    
class CartsAPI(Resource):
    @roles_required('user')
    def get(self):
        carts = Cart.query.filter_by(user_id=current_user.id).all()
        return marshal(carts, cart_fields), 200
    
    @roles_required('user')
    def post(self, product_id):
        args = purchase_parser.parse_args()
        user_id = current_user.id
        # product_id = args.get('product_id',None)
        quantity = args.get('quantity',None)
        if any(field is None for field in (product_id, quantity)):
            return {"message":"One or more fields are empty"}, 400
        product = Product.query.get(product_id)
        if not product:
            return {"message":"Product not exists"}, 400
        if product.availability < int(quantity):
            return {"message":"The selected quantity is more than the available stock"}, 400
        cart_exist = Cart.query.filter_by(user_id=user_id,product_id=product_id).first()
        if cart_exist:
            cart_exist.quantity += int(quantity)
        else:
            cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart)
        db.session.commit()
        # return marshal(cart, cart_fields), 201
        return {"message":f"{product.name} added to cart successfully"}, 201
    
    @roles_required('user')
    def delete(self, id):
        cart = Cart.query.get(id)
        if not cart:
            return {"message":"Invalid ID"}, 404
        db.session.delete(cart)
        db.session.commit()
        return {"message":"Item deleted successfully from the cart"}, 200
    
    @roles_required('user')
    def put(self, id):
        cart = Cart.query.get(id)
        if not cart:
            return {"message":"Invalid ID"}, 404
        args = purchase_parser.parse_args()
        user_id = current_user.id
        product_id = args.get('product_id',None)
        quantity = args.get('quantity',None)
        if any(field is None for field in (user_id, product_id, quantity)):
            return {"message":"One or more fields are empty"}, 400
        product = Product.query.get(product_id)
        if not product:
            return {"message":"Product not exists"}, 400
        if product.availability < int(quantity):
            return {"message":"The selected quantity is more than the available stock"}, 400
        cart.product_id = product_id
        cart.quantity = quantity
        db.session.commit()
        return marshal(cart, cart_fields), 200
    
class PurchasesAPI(Resource):
    @roles_required('user')
    def get(self):
        purchases = Purchase.query.filter_by(user_id=current_user.id).all()
        return marshal(purchases, purchase_fields), 200
    
    @roles_required('user')
    def post(self):
        args = purchase_parser.parse_args()
        user_id = current_user.id
        product_id = args.get('product_id',None)
        quantity = args.get('quantity',None)
        print(product_id,quantity)
        if any(field is None for field in (user_id, product_id, quantity)):
            return {"message":"One or more fields are empty"}, 400
        product = Product.query.get(product_id)
        if not product:
            return {"message":"Product not exists"}, 400
        if product.availability < int(quantity):
            return {"message":"The selected quantity is more than the available stock"}, 400
        purchase = Purchase(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(purchase)
        product.availability -= int(quantity)
        db.session.commit()
        return marshal(purchase, purchase_fields), 201

approval_fields = {
    'pending_managers': fields.Nested(user_fields),
    'pending_categories': fields.Nested(category_fields)
}

class AdminAPI(Resource):
    @roles_required('admin')
    def get(self):
        pending_managers = User.query.filter_by(active=False).all()
        pending_categories = Category.query.filter_by(active=False).all()
        response = {'pending_managers':pending_managers,'pending_categories':pending_categories}
        return marshal(response, approval_fields), 200
 