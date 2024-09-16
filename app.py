from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError
from sqlalchemy import select
from password import password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{password}@localhost/e_commerce_db' 
db = SQLAlchemy(app)
ma = Marshmallow(app)

#Customer Class and Schemas#

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ('name', 'email', 'phone', 'id')

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')

#Example format in Postman (add/update)

# {

#     "name":"XXXXXX",
#     "email":"YYYYYYY",
#     "phone":"#######"

# }

#CustomerAccount Class and Schemas#

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.String(required=True)

    class Meta:
        fields = ('id', 'username', 'password', 'customer_id')

customeraccount_schema = CustomerAccountSchema()
customeraccounts_schema = CustomerAccountSchema(many=True)

#One to One

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False) 
    #uselist=False means treats as single item (One customer per account in this scenario)

#Example format in Postman (add/update)
#{

    #"username": "XXXXXX",
    #"password": "YYYYYY",
    #"customer_id": "1"

#}

#Product Class and Schemas#

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # orders = db.relationship('Order', secondary=order_product, backref=db.backref('products'))

class ProductSchema(ma.Schema):
    id = fields.Integer(required=False)
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ('id','name', 'price')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

#Many to Many

#association table
order_product = db.Table('Order_Product',
    db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key = True),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key = True)
)

#Order Class and Schemas#

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    products = db.relationship('Product', secondary=order_product, backref=db.backref('orders', lazy='dynamic'))

#Example format in Postman (add/update)
#{

    #"order_date": "YYYY/MM/DD",
    #"delivery_date": "YYYY/MM/DD",
    #"customer_id": "1"
    #"product_id": "1"

#}

class OrderSchema(ma.Schema):
    id = fields.Integer(required=False)
    order_date = fields.String(required=True)
    delivery_date = fields.String(required=True)
    customer_id = fields.String(required=True)
    products = fields.List(fields.Nested(ProductSchema))

    class Meta:
        fields = ('id', 'order_date', 'delivery_date', 'customer_id', 'products')

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

#Example format in Postman (add/update)
# {

#     "name":"XXXXXX",
#     "price":"YYYYYYY",

# }

#Customer Functions#

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'New customer added successfully'}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({'message':'Customer details updated successfully'}), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message':'Customer removed successfully'}), 200

#Customer Account Functions#

@app.route('/customeraccounts', methods=['GET'])
def get_customeraccounts():
    customeraccounts = CustomerAccount.query.all()
    return customeraccounts_schema.jsonify(customeraccounts)

@app.route('/customeraccounts', methods=['POST'])
def add_customeraccount():
    try:
        customeraccount_data = customeraccount_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_customeraccount = CustomerAccount(username=customeraccount_data['username'], password=customeraccount_data['password'], customer_id=customeraccount_data['customer_id'])
    db.session.add(new_customeraccount)
    db.session.commit()
    return jsonify({'message': 'New customer account added successfully'}), 201

@app.route('/customeraccounts/<int:id>', methods=['PUT'])
def update_customeraccount(id):
    customeraccount = CustomerAccount.query.get_or_404(id)
    try:
        customeraccount_data = customeraccount_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customeraccount.username = customeraccount_data['username']
    customeraccount.password = customeraccount_data['password']
    customeraccount.customer_id = customeraccount_data['customer_id']
    db.session.commit()
    return jsonify({'message':'Customer account details updated successfully'}), 200

@app.route('/customeraccounts/<int:id>', methods=['DELETE'])
def delete_customeraccount(id):
    customeraccount = CustomerAccount.query.get_or_404(id)
    db.session.delete(customeraccount)
    db.session.commit()
    return jsonify({'message':'Customer account removed successfully'}), 200

#Product Functions#

@app.route('/products', methods=['GET'])
def get_product():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/by-id', methods=['GET']) #/by-id?id=1    (example)
def view_by_product_id():
    id = request.args.get('id')
    product = Product.query.filter(Product.id == id).first()
    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product not found"}), 404


@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'New product added successfully'}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({'message':'Product details updated successfully'}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message':'Product removed successfully'}), 200

#Order Functions#

@app.route('/orders', methods=['GET'])
def get_orders():
    query = select(Order)
    result = db.session.execute(query).scalars()
    products = result.all() 
    return orders_schema.jsonify(products) 

@app.route('/orders', methods=['POST']) 
def add_order():
    try:
        json_order = request.json
        products = json_order.pop('products', [])
        if not products:
            return jsonify({'Error': 'cannot place order without products.'}), 400
        order_data = order_schema.load(json_order)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_order = Order(order_date=order_data['order_date'], delivery_date=order_data['delivery_date'], customer_id=order_data['customer_id'])
    for product in products:
        item = Product.query.filter_by(id = product).first()
        new_order.products.append(item)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'New order placed successfully'}), 201    

@app.route('/orders/<int:order_id>', methods=['PUT']) 
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    try:
        json_order = request.json
        products = json_order.pop('products', [])
        if not products:
            return jsonify({'Error': 'cannot update order without products.'}), 400
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    order.order_date = order_data['order_date']
    order.delivery_date = order_data['delivery_date']
    order.customer_id = order_data['customer_id']
    order.products.clear()
    for product in products:
        item = Product.query.filter_by(id = product).first()
        order.products.append(item)

    db.session.commit()
    return jsonify({'message':'Order details updated successfully'}), 200

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message':'Order removed successfully'}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
