from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'ecommerce_db',  # Replace with your MongoDB database name
    'host': 'localhost',
    'port': 27017  # Replace with your MongoDB port
}
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Replace with your secret key
db = MongoEngine(app)
jwt = JWTManager(app)

# Define User, Product, and Review models (MongoEngine documents).
class User(db.Document):
    username = db.StringField(unique=True, required=True)
    password = db.StringField(required=True)

class Product(db.Document):
    name = db.StringField(required=True)
    # Add other product fields (barcode, brand, description, price, available, etc.)

class Review(db.Document):
    user_id = db.ReferenceField(User, required=True)
    product_id = db.ReferenceField(Product, required=True)
    rating = db.FloatField(required=True)
    comment = db.StringField()

# Registration API
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], password=data['password'])
    new_user.save()
    return jsonify({"message": "User registered successfully"})

# Login API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.objects(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token})
    return jsonify({"message": "Invalid credentials"}), 401

# Product Upload API
@app.route('/api/upload-product-csv', methods=['POST'])
@jwt_required()
def upload_product_csv():
    data = request.get_json()
    # Implement logic to parse CSV file and store product data in the database.
    # Ensure that only admin users with a valid JWT token can access this endpoint.
    # For demonstration purposes, let's assume products are added directly.
    product = Product(name=data['name'])
    product.save()
    return jsonify({"message": "CSV file uploaded successfully"})

# Product Review API
@app.route('/api/product/<string:product_id>/review', methods=['POST'])
@jwt_required()
def add_product_review(product_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    review = Review(user_id=current_user_id, product_id=product_id, rating=data['rating'], comment=data['comment'])
    review.save()
    return jsonify({"message": "Review added successfully"})

# Product View Pagination API
@app.route('/api/products', methods=['GET'])
def get_paginated_products():
    page = int(request.args.get('page', default=1))
    page_size = int(request.args.get('page_size', default=10))
    sort_by = request.args.get('sort_by', default='name')

    # Implement logic to retrieve and paginate products based on sorting criteria.
    # Return a paginated list of products.
    products = Product.objects().order_by(sort_by).skip((page - 1) * page_size).limit(page_size)
    return jsonify({"products": [product.to_json() for product in products]})

if __name__ == '__main__':
    app.run(debug=True)