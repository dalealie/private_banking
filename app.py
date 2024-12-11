from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "private_banking"
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
            "employee_ID": employee[0]
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
            "address_ID": client[1], 
            "bank_ID": client[2],
            "client_Manager_Employee_ID": client[3]
        }
        for client in clients
    ]
    
    return jsonify(clients_list), 200

@app.route("/cash_flows")
def get_cash_flows():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Cash_Flows")
    cash_flows = cursor.fetchall()
    if not cash_flows:
        return handle_error("No cash flows found", 404)

    cash_flows_list = [
        {
            "cash_Flow_ID": cash_flow[0], 
            "client_ID": cash_flow[1]
        }
        for cash_flow in cash_flows
    ]
    
    return jsonify(cash_flows_list), 200

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
            "product_Type_Code": product[1]
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
            "contact_ID": transaction[2], 
            "employee_ID": transaction[3], 
            "partner_ID": transaction[4], 
            "product_ID": transaction[5], 
            "stock_Symbol": transaction[6], 
            "transaction_Date": transaction[7], 
            "transaction_Type_Code": transaction[8]
        }
        for transaction in transactions
    ]
    
    return jsonify(transactions_list), 200

if __name__ == '__main__':
    app.run(debug=True)