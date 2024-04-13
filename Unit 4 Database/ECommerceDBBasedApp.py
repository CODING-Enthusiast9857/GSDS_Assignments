from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb+srv://[Provide your credentials:password]#@cluster0.f1y0blh.mongodb.net/?retryWrites=true&w=majority") 

db = client["e-commerce"]  # Replace with your MongoDB database name
products_collection = db["products"]
carts_collection = db["carts"]

# Initialize a list of products with unique IDs
products = [
    {
        'name': 'Mac Book Pro',
        'price': 45.55,
        'description': 'Amazing laptop with awesome security'
    },
    {
        'name': 'iPhone 11',
        'price': 90.55,
        'description': 'Amazing phone with awesome security'
    },
    {
        'name': 'iPhone 11 Pro',
        'price': 120.55,
        'description': 'Amazing phone with awesome security'
    },
    {
        'name': 'Tablet',
        'price': 540.55,
        'description': 'Amazing tablet with awesome security'
    }

]

# Initialize an empty cart as a global variable
#products_collection.insert_many(products)

# Define a collection to store cart items (for demonstration purposes)
cart = []

# Function to display all products from the MongoDB database
@app.route('/display_products', methods=['GET'])
def display_products():
    products = list(products_collection.find({}, {"_id": 0}))
    return jsonify({'products': products})

# Function to display a product by ID from the MongoDB database
@app.route('/display_product/<int:product_id>', methods=['GET'])
def display_product(product_id):
    product = products_collection.find_one({"prod_id": product_id}, {"_id": 0})
    if product:
        return jsonify({'product': product})
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/add_products', methods=['POST'])
def add_products():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No product data provided in the request'}), 400

        # Insert the products into the MongoDB collection
        products_collection.insert_many(data)

        return jsonify({'message': 'Products added successfully'})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Function to view the user's cart
@app.route('/cart/view', methods=['GET'])
def view_cart():
    # Get the user_id from the query parameter
    user_id = request.args.get('user_id')

    # Check if user_id is provided
    if user_id is None:
        return jsonify({'error': 'user_id parameter is missing'}), 400

    try:
        # Retrieve the user's cart from the carts collection in MongoDB
        user_cart = carts_collection.find_one({"user_id": user_id}, {"_id": 0, "user_id": 0})

        if user_cart is None:
            return jsonify({'message': 'Cart is empty'})

        # Create a list to store cart items with additional details
        cart_items = []
        total_amount = 0

        # Iterate through the cart items
        for product_id, quantity in user_cart.items():
            if product_id != "user_id":  # Skip the user_id field
            # Try to find the product by its id in the products collection
                product = products_collection.find_one({"prod_id": int(product_id)}, {"_id": 0})

                if product:
                    item_total = product['price'] * quantity
                    total_amount += item_total
                    cart_items.append({
                        'product_id': product_id,
                        'name': product['name'],
                        'price': product['price'],
                        'quantity': quantity,
                        'item_total': item_total
                    })

        # Prepare the response
        response_data = {
            'cart_items': cart_items,
            'total_amount': total_amount
        }

        # Return the response as JSON
        return jsonify(response_data)

    except Exception as e:
        # Handle any exceptions that may occur
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


# Function to add a product to the user's cart
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    product = products_collection.find_one({"prod_id": product_id}, {"_id": 0})

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Update the user's cart in the carts collection in MongoDB
    # If the user does not have a cart, create one
    carts_collection.update_one(
        {"user_id": user_id},
        {"$set": {f"{product_id}": quantity}},
        upsert=True
    )

    return jsonify({'message': 'Product added to the cart'})


# Function to delete the user's cart
@app.route('/cart/delete', methods=['DELETE'])
def delete_cart():
    # Get the user_id from the query parameter
    user_id = request.args.get('user_id')

    # Check if user_id is provided
    if user_id is None:
        return jsonify({'error': 'user_id parameter is missing'}), 400

    try:
        # Delete the user's cart from the carts collection in MongoDB
        result = carts_collection.delete_one({"user_id": user_id})

        if result.deleted_count == 1:
            return jsonify({'message': 'Cart deleted successfully'})
        else:
            return jsonify({'message': 'Cart not found'})

    except Exception as e:
        # Handle any exceptions that may occur
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)