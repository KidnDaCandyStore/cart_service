# ASSIGNENT 2: 
# DAVID NEWMAN
# CMSC 455
# cart_service.py

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cart.db'
db = SQLAlchemy(app)


# SERVICE URL FOR LINKING TO PRODUCT SERVICE ON RENDER: 
PRODUCT_SERVICE_URL = 'https://product-service-7ft0.onrender.com'


# CART ITEM: DATA STRUCTURE: 
class CartItem(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    user_id     = db.Column(db.String(50))
    product_id  = db.Column(db.Integer)
    quantity    = db.Column(db.Integer)


# GET CART VIA USER ID: FUNCTION: 
@app.route('/cart/<user_id>', methods = ['GET'])
def get_cart(user_id):
    # RETRIEVE ALL CART ITEMS: 
    cart_items = CartItem.query.filter_by(user_id = user_id).all()
    
    # LOOP THROUGH ALL ITEMS IN CART TO APPEND THE DATA INTO THE RESULT ARRAY:
    result = []
    for item in cart_items:
        # FETCH THE SPECIFIC PRODUCT INTO THE PRODUCT VAR: 
        product = requests.get(f"{PRODUCT_SERVICE_URL}/products/{item.product_id}").json()
        # APPEND THE RESULT ARRAY WITH THE PRODUCT INFO: 
        result.append({
            'product_name': product['name'],
            'quantity': item.quantity,
            'total_price': product['price'] * item.quantity
        })
    # OUTPUT THE RESULT VIA JSON: 
    return jsonify(result)


# ADD TO CART: FUNCTION: 
@app.route('/cart/<user_id>/add/<int:product_id>', methods = ['POST'])
def add_to_cart(user_id, product_id):
    # QUANTITY IS 1 FOR SIMPLICITY: 
    cart_item = CartItem(user_id = user_id, product_id = product_id, quantity = 1)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": f"PRODUCT ID#: {product_id} WAS SUCCESSFULLY ADDED TO CART!"}), 201


# REMOVE FROM CART: FUNCTION: 
@app.route('/cart/<user_id>/remove/<int:product_id>', methods = ['POST'])
def remove_from_cart(user_id, product_id):
    # QUANTITY IS 1 FOR SIMPLICITY: 
    cart_item = CartItem.query.filter_by(user_id = user_id, product_id = product_id).first_or_404()
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.session.commit()
    else:
        db.session.delete(cart_item)
        db.session.commit()
    return jsonify({"message": f"PRODUCT ID#: {product_id} WAS SUCCESSFULLY REMOVED FROM CART!"}), 200


# CREATE DATABASE TABLES: FUNCTION: 
@app.before_first_request
def create_tables():
    db.create_all()


# RUN THE APP! 
if __name__ == '__main__':
    # CART SERVICE RUNNING ON NEXT OVER PORT!
    app.run(port = 5001, debug = True)