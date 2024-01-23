from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_restful import Api
from flask_cors import CORS, cross_origin
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import *
from flask_caching import Cache
from application import workers
import random, string

app = None
api = None
celery = None
cache = None            

# Create app
def create_app():
    app = Flask(__name__) 
    app.config.from_object(LocalDevelopmentConfig)
    app.app_context().push()

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    db.init_app(app)
    app.app_context().push()
    db.create_all()

    user = User.query.filter_by(email='admin@gmail.com').first()
    if not user:
        fs_uniquifier = ''.join(random.choices(string.ascii_letters,k=10))
        user = User(email='admin@gmail.com', username='admin', name='admin', password=hash_password("admin"), fs_uniquifier=fs_uniquifier)
        user.roles.append(Role(name='admin'))
        db.session.add(user)

        manager_role = Role(name='manager')
        user_role = Role(name='user')
        db.session.add(manager_role)
        db.session.add(user_role)
        db.session.commit()

    api = Api(app)
    app.app_context().push()
    celery = workers.celery

    # Update with configuration
    celery.conf.update(
        broker_url = app.config["CELERY_BROKER_URL"],
        result_backend = app.config["CELERY_RESULT_BACKEND"]
    )

    celery.Task = workers.ContextTask

    CORS(app, supports_credentials=True)
    app.config['CORS_HEADERS'] = 'application/json'
    cache = Cache(app)
    app.app_context().push()
    return app, api, celery, cache

app,api,celery, cache = create_app()

from application.controllers import *
from application.api import *

api.add_resource(UserAPI, "/api/getuser", "/api/adduser")
api.add_resource(CategoryAPI, "/api/categories", "/api/category/<int:id>", "/api/addcategory")
api.add_resource(ProductAPI, "/api/products","/api/product/<int:id>","/api/addproduct")
api.add_resource(PurchaseAPI, "/api/purchases","/api/addpurchase")
api.add_resource(CartAPI, "/api/carts", "/api/cart/<int:id>", "/api/addtocart/<int:product_id>")

if __name__ == '__main__':
    app.run()