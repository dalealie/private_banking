from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "mini_private_banking"
mysql = MySQL(app)

def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

@app.route("/")
def hello_world():
    return "WELCOME TO PRIVATE BANKING DATABASE"

@app.route("/employees")
def get_employees():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Employees")
    employees = cursor.fetchall()
    if not employees:
        return handle_error("No employees found", 404)
    employees_list = [
        {
            "Employee_ID": employee[0],
            "Name": employee[1]
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
            "Client_ID": client[0],
            "Name": client[1],
            "Email": client[2],
            "Phone": client[3],
            "Client_Manager_Employee_ID": client[4]
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
            "Product_ID": product[0],
            "Product_Type": product[1]
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
            "Transaction_ID": transaction[0],
            "Client_ID": transaction[1],
            "Product_ID": transaction[2],
            "Transaction_Amount": transaction[3],
            "Transaction_Date": transaction[4]
        }
        for transaction in transactions
    ]
    
    return jsonify(transactions_list), 200

if __name__ == '__main__':
    app.run(debug=True)