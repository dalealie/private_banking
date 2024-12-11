# Mini Private Banking Database API

## Description
A Flask-based REST API for managing employees, clients, products, transactions, and cash flows in the `mini_private_banking` database.

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
To configure the database:
1. Upload the ```mini_private_banking``` MySQL database to your server or local machine.
2. Update the database configuration in the Flask app with your database connection details.

Environment variables needed:
- ```MYSQL_HOST```: The host for the MySQL database (e.g., localhost or IP address of the database server)
- ```MYSQL_USER```: MySQL username (e.g., root)
- ```MYSQL_PASSWORD```: MySQL password
- ```MYSQL_DB```: Name of the database (e.g., mini_private_banking)



## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /	| GET	| Welcome message |
| /employees	| GET	| List all employees |
| /employees	| POST	| Add a new employee |
| /employees/<employee_id>	| PUT	| Update an employee's details |
| /employees/<employee_id>	| DELETE	| Delete an employee |
| /clients	| GET	| List all clients |
| /clients	| POST	| Add a new client |
| /clients/<client_id>	| PUT	| Update a client's details |
| /clients/<client_id>	| DELETE	| Delete a client |
| /products	| GET	| List all products |
| /products	| POST	| Add a new product |
| /products/<product_id>	| PUT	| Update a product's details |
| /products/<product_id>	| DELETE	| Delete a product |
| /transactions	| GET	| List all transactions |
| /transactions	| POST	| Add a new transaction |
| /transactions/<transaction_id>	| PUT	| Update a transaction's details |
| /transactions/<transaction_id>	| DELETE	| Delete a transaction |
| /cash_flows	| GET	| List all cash flows |
| /cash_flows	| POST	| Add a new cash flow |
| /cash_flows/<cash_flow_id>	| PUT	| Update a cash flow's details |
| /cash_flows/<cash_flow_id>	| DELETE	| Delete a cash flow |

## Git Commit Guidelines
Use conventional commits:
```bash
feat: add user authentication
feat: add employee management feature
fix: resolve database connection issue
docs: update API documentation
test: add transaction validation tests
feat: add user authentication
```