import json
import datetime
import jwt
from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "mini_private_banking"
app.config["SECRET_KEY"] = "daless"

mysql = MySQL(app)
bcrypt = Bcrypt(app)

def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

@app.route("/")
def hello_world():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Private Banking Database</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 0;
                text-align: center;
                padding-top: 50px;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 1.2em;
                margin: 10px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #2980b9;
            }
        </style>
    </head>
    <body>
        <button onclick="window.location.href='/employees'">Employees</button>
        <button onclick="window.location.href='/clients'">Clients</button>
        <button onclick="window.location.href='/products'">Products</button>
        <button onclick="window.location.href='/transactions'">Transactions</button>
    </body>
    </html>
    """


def validate_token():
    token = request.headers.get("x-access-token")
    if not token:
        return None, handle_error("Token is missing!", 401)
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        current_user = {"user_id": data["user_id"], "role": data["role"]}
        return current_user, None
    except Exception:
        return None, handle_error("Token is invalid!", 401)

def validate_role(current_user, valid_roles):
    if isinstance(valid_roles, str):
        valid_roles = [valid_roles]
    
    if current_user["role"] not in valid_roles:
        return jsonify({"error": "Unauthorized access"}), 403
    return None

users_data = {
    "users": []
}

def save_to_json():
    with open("users.json", "w") as f:
        json.dump(users_data, f)

def load_from_json():
    global users_data
    try:
        with open("users.json", "r") as f:
            users_data = json.load(f)
    except FileNotFoundError:
        save_to_json()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password") or not data.get("role"):
        return handle_error("Missing required fields: username, password, and role are mandatory", 400)
    username = data["username"]
    password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    role = data["role"]
    load_from_json()
    for user in users_data["users"]:
        if user["username"] == username:
            return handle_error("Username already exists", 400)
    new_user = {"username": username, "password": password, "role": role}
    users_data["users"].append(new_user)
    save_to_json()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return handle_error("Missing required fields: username and password are mandatory", 400)
    username = data["username"]
    password = data["password"]
    load_from_json()
    for user in users_data["users"]:
        if user["username"] == username and bcrypt.check_password_hash(user["password"], password):
            token = jwt.encode(
                {
                    "user_id": username,
                    "role": user["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            return jsonify({"token": token}), 200
    return handle_error("Invalid credentials", 401)

@app.route("/employees")
def get_employees():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Employees")
    employees = cursor.fetchall()
    if not employees:
        return handle_error("No employees found", 404)
    
    employees_list = [
        {
            "employee_ID": employee[0], 
            "name": employee[1]
        }
        for employee in employees
    ]
    
    return jsonify(employees_list), 200

@app.route("/clients")
def get_clients():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Clients")
    clients = cursor.fetchall()
    if not clients:
        return handle_error("No clients found", 404)

    clients_list = [
        {
            "client_ID": client[0], 
            "name": client[1], 
            "email": client[2], 
            "phone": client[3],
            "client_Manager_Employee_ID": client[4]
        }
        for client in clients
    ]
    
    return jsonify(clients_list), 200

@app.route("/products")
def get_products():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    if not products:
        return handle_error("No products found", 404)

    products_list = [
        {
            "product_ID": product[0], 
            "product_Type": product[1]
        }
        for product in products
    ]
    
    return jsonify(products_list), 200

@app.route("/transactions")
def get_transactions():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Transactions")
    transactions = cursor.fetchall()
    if not transactions:
        return handle_error("No transactions found", 404)

    transactions_list = [
        {
            "transaction_ID": transaction[0],
            "client_ID": transaction[1], 
            "product_ID": transaction[2], 
            "transaction_Amount": transaction[3], 
            "transaction_Date": transaction[4]
        }
        for transaction in transactions
    ]
    
    return jsonify(transactions_list), 200

@app.route("/employees", methods=["POST"])
def add_employee():
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
    
    data = request.get_json()
    employee_id = data.get('employee_ID')
    name = data.get('name')
    
    if not employee_id or not name:
        return handle_error("Employee ID and name are required", 400)
    
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO Employees (Employee_ID, Name) VALUES (%s, %s)", (employee_id, name))
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Employees WHERE Employee_ID = %s", (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        return handle_error("Failed to retrieve the added employee", 500)

    return jsonify({
        "employee_ID": employee[0], 
        "name": employee[1]
    }), 201

@app.route("/clients", methods=["POST"])
def add_client():
    current_user, error = validate_token()
    if error:
        return error
     
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
       
    data = request.get_json()
    client_id = data.get('client_ID')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    client_manager_employee_id = data.get('client_Manager_Employee_ID')

    if not all([client_id, name, email, phone, client_manager_employee_id]):
        return handle_error("Missing required fields", 400)
    
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Clients (Client_ID, Name, Email, Phone, Client_Manager_Employee_ID) VALUES (%s, %s, %s, %s, %s)", 
        (client_id, name, email, phone, client_manager_employee_id)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Clients WHERE Client_ID = %s", (client_id,))
    client = cursor.fetchone()

    if not client:
        return handle_error("Failed to retrieve the added client", 500)

    return jsonify({
        "client_ID": client[0], 
        "name": client[1], 
        "email": client[2], 
        "phone": client[3],
        "client_Manager_Employee_ID": client[4]
    }), 201

@app.route("/products", methods=["POST"])
def add_product():
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
   

    data = request.get_json()
    product_id = data.get('product_ID')
    product_type = data.get('product_Type')

    if not all([product_id, product_type]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Products (Product_ID, Product_Type) VALUES (%s, %s)", 
        (product_id, product_type)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Products WHERE Product_ID = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        return handle_error("Failed to retrieve the added product", 500)

    return jsonify({
        "product_ID": product[0], 
        "product_Type": product[1]
    }), 201

@app.route("/transactions", methods=["POST"])
def add_transaction():
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
   
  
    data = request.get_json()
    transaction_id = data.get('transaction_ID')
    client_id = data.get('client_ID')
    product_id = data.get('product_ID')
    transaction_amount = data.get('transaction_Amount')
    transaction_date = data.get('transaction_Date')

    if not all([transaction_id, client_id, product_id, transaction_amount, transaction_date]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Transactions (Transaction_ID, Client_ID, Product_ID, Transaction_Amount, Transaction_Date) VALUES (%s, %s, %s, %s, %s)",
        (transaction_id, client_id, product_id, transaction_amount, transaction_date)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Transactions WHERE Transaction_ID = %s", (transaction_id,))
    transaction = cursor.fetchone()

    if not transaction:
        return handle_error("Failed to retrieve the added transaction", 500)

    return jsonify({
        "transaction_ID": transaction[0], 
        "client_ID": transaction[1], 
        "product_ID": transaction[2], 
        "transaction_Amount": transaction[3], 
        "transaction_Date": transaction[4]
    }), 201

@app.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
   
  
    data = request.get_json()
    name = data.get('name')

    if not name:
        return handle_error("Name is required", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE Employees SET Name = %s WHERE Employee_ID = %s", 
        (name, employee_id)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Employees WHERE Employee_ID = %s", (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        return handle_error("Employee not found", 404)

    return jsonify({
        "employee_ID": employee[0], 
        "name": employee[1]
    }), 200

@app.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
   
  
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    client_manager_employee_id = data.get('client_Manager_Employee_ID')

    if not all([name, email, phone, client_manager_employee_id]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE Clients SET Name = %s, Email = %s, Phone = %s, Client_Manager_Employee_ID = %s WHERE Client_ID = %s", 
        (name, email, phone, client_manager_employee_id, client_id)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Clients WHERE Client_ID = %s", (client_id,))
    client = cursor.fetchone()

    if not client:
        return handle_error("Client not found", 404)

    return jsonify({
        "client_ID": client[0], 
        "name": client[1], 
        "email": client[2], 
        "phone": client[3],
        "client_Manager_Employee_ID": client[4]
    }), 200

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
   
    data = request.get_json()
    product_type = data.get('product_Type')

    if not product_type:
        return handle_error("Product Type is required", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE Products SET Product_Type = %s WHERE Product_ID = %s", 
        (product_type, product_id)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Products WHERE Product_ID = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        return handle_error("Product not found", 404)

    return jsonify({
        "product_ID": product[0], 
        "product_Type": product[1]
    }), 200

@app.route("/transactions/<int:transaction_id>", methods=["PUT"])
def update_transaction(transaction_id):
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
     
    data = request.get_json()
    client_id = data.get('client_ID')
    product_id = data.get('product_ID')
    transaction_amount = data.get('transaction_Amount')
    transaction_date = data.get('transaction_Date')

    if not all([client_id, product_id, transaction_amount, transaction_date]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE Transactions SET Client_ID = %s, Product_ID = %s, Transaction_Amount = %s, Transaction_Date = %s WHERE Transaction_ID = %s",
        (client_id, product_id, transaction_amount, transaction_date, transaction_id)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Transactions WHERE Transaction_ID = %s", (transaction_id,))
    transaction = cursor.fetchone()

    if not transaction:
        return handle_error("Transaction not found", 404)

    return jsonify({
        "transaction_ID": transaction[0], 
        "client_ID": transaction[1], 
        "product_ID": transaction[2], 
        "transaction_Amount": transaction[3], 
        "transaction_Date": transaction[4]
    }), 200

@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
     
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Employees WHERE Employee_ID = %s", (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        return handle_error("Employee not found", 404)

    cursor.execute("DELETE FROM Employees WHERE Employee_ID = %s", (employee_id,))
    mysql.connection.commit()

    return jsonify({"message": f"Employee with ID {employee_id} has been deleted."}), 200

@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
     
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Clients WHERE Client_ID = %s", (client_id,))
    client = cursor.fetchone()

    if not client:
        return handle_error("Client not found", 404)

    cursor.execute("DELETE FROM Clients WHERE Client_ID = %s", (client_id,))
    mysql.connection.commit()

    return jsonify({"message": f"Client with ID {client_id} has been deleted."}), 200

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    current_user, error = validate_token()
    if error:
        return error
     
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Products WHERE Product_ID = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        return handle_error("Product not found", 404)

    cursor.execute("DELETE FROM Products WHERE Product_ID = %s", (product_id,))
    mysql.connection.commit()

    return jsonify({"message": f"Product with ID {product_id} has been deleted."}), 200

@app.route("/transactions/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    current_user, error = validate_token()
    if error:
        return error
    
    required_role = "admin"
    role_error = validate_role(current_user, required_role)
    if role_error:
        return role_error 
     
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Transactions WHERE Transaction_ID = %s", (transaction_id,))
    transaction = cursor.fetchone()

    if not transaction:
        return handle_error("Transaction not found", 404)

    cursor.execute("DELETE FROM Transactions WHERE Transaction_ID = %s", (transaction_id,))
    mysql.connection.commit()

    return jsonify({"message": f"Transaction with ID {transaction_id} has been deleted."}), 200


if __name__ == "__main__":
    app.run(debug=True)