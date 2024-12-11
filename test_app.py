import pytest
from app import app

@pytest.fixture
def mock_db(mocker):

    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    

    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None
    mock_cursor.rowcount = 1
    
    return mock_cursor

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"WELCOME TO PRIVATE BANKING DATABASE" in response.data

def test_get_employees_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/employees')

    assert response.status_code == 404
    assert b"No employees found" in response.data

def test_get_employees(mock_db):
    mock_db.fetchall.return_value = [(1, 'John Doe'), (2, 'Jane Smith')]

    client = app.test_client()
    response = client.get('/employees')

    assert response.status_code == 200
    assert b"John Doe" in response.data
    assert b"Jane Smith" in response.data

def test_add_employee_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/employees', json={})

    assert response.status_code == 400
    assert b"Employee ID and name are required" in response.data

def test_add_employee_success(mock_db):
    mock_db.rowcount = 1
    mock_db.fetchone.return_value = (1, 'John Doe')

    client = app.test_client()
    response = client.post('/employees', json={'employee_ID': 1, 'name': 'John Doe'})

    assert response.status_code == 201
    assert b"employee_ID" in response.data
    assert b"1" in response.data
    assert b"John Doe" in response.data
    
def test_update_employee_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/employees/1', json={})

    assert response.status_code == 400
    assert b"Name is required" in response.data

def test_update_employee_not_found(mock_db):
    mock_db.rowcount = 0

    client = app.test_client()
    response = client.put('/employees/999', json={'name': 'Updated Name'})

    assert response.status_code == 404
    assert b"Employee not found" in response.data

def test_delete_employee_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.delete('/employees/999')

    assert response.status_code == 404
    assert b"Employee not found" in response.data

def test_delete_employee_success(mock_db):
    mock_db.fetchone.return_value = (1, 'John Doe')
    mock_db.rowcount = 1

    client = app.test_client()
    response = client.delete('/employees/1')

    assert response.status_code == 200
    assert b"Employee with ID 1 has been deleted." in response.data

def test_get_clients_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/clients')

    assert response.status_code == 404
    assert b"No clients found" in response.data

def test_get_clients(mock_db):
    mock_db.fetchall.return_value = [(1, 'John Doe', 'john@example.com', '1234567890', 1)]
    client = app.test_client()
    response = client.get('/clients')
    
    assert response.status_code == 200
    assert b'John Doe' in response.data
    assert b'john@example.com' in response.data

def test_add_client_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/clients', json={})

    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_add_client_success(mock_db):
    mock_db.rowcount = 1
    mock_db.fetchone.return_value = (1, 'John Doe', 'john@example.com', '1234567890', 1)

    client = app.test_client()
    response = client.post('/clients', json={
        'client_ID': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone': '1234567890', 'client_Manager_Employee_ID': 1
    })

    assert response.status_code == 201
    assert b"client_ID" in response.data
    assert b"1" in response.data
    assert b"John Doe" in response.data

def test_delete_client_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.delete('/clients/999')

    assert response.status_code == 404
    assert b"Client not found" in response.data

def test_delete_client_success(mock_db):
    mock_db.fetchone.return_value = (1, 'John Doe', 'john@example.com', '1234567890', 1)
    mock_db.rowcount = 1

    client = app.test_client()
    response = client.delete('/clients/1')

    assert response.status_code == 200
    assert b"Client with ID 1 has been deleted." in response.data
    
def test_get_products_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/products')

    assert response.status_code == 404
    assert b"No products found" in response.data

def test_get_products(mock_db):
    mock_db.fetchall.return_value = [(1, 'Product A')]
    client = app.test_client()
    response = client.get('/products')

    assert response.status_code == 200
    assert b'Product A' in response.data

def test_add_product_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/products', json={})

    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_add_product_success(mock_db):
    mock_db.rowcount = 1
    mock_db.fetchone.return_value = (1, 'Product A')

    client = app.test_client()
    response = client.post('/products', json={'product_ID': 1, 'product_Type': 'Product A'})

    assert response.status_code == 201
    assert b"product_ID" in response.data
    assert b"1" in response.data
    assert b"Product A" in response.data

def test_delete_product_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.delete('/products/999')

    assert response.status_code == 404
    assert b"Product not found" in response.data

def test_delete_product_success(mock_db):
    mock_db.fetchone.return_value = (1, 'Product A')
    mock_db.rowcount = 1

    client = app.test_client()
    response = client.delete('/products/1')

    assert response.status_code == 200
    assert b"Product with ID 1 has been deleted." in response.data

def test_get_transactions_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/transactions')

    assert response.status_code == 404
    assert b"No transactions found" in response.data

def test_get_transactions(mock_db):
    mock_db.fetchall.return_value = [(1, 1, 1, 100, '2024-12-11')]
    client = app.test_client()
    response = client.get('/transactions')

    assert response.status_code == 200
    assert b'100' in response.data
    assert b'2024-12-11' in response.data

def test_add_transaction_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/transactions', json={})

    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_add_transaction_success(mock_db):
    mock_db.rowcount = 1
    mock_db.fetchone.return_value = (1, 1, 1, 100, '2024-12-11')

    client = app.test_client()
    response = client.post('/transactions', json={
        'transaction_ID': 1, 'client_ID': 1, 'product_ID': 1, 'transaction_Amount': 100, 'transaction_Date': '2024-12-11'
    })

    assert response.status_code == 201
    assert b"transaction_ID" in response.data
    assert b"1" in response.data
    assert b"100" in response.data

def test_delete_transaction_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.delete('/transactions/999')

    assert response.status_code == 404
    assert b"Transaction not found" in response.data

def test_delete_transaction_success(mock_db):
    mock_db.fetchone.return_value = (1, 1, 1, 100, '2024-12-11')
    mock_db.rowcount = 1

    client = app.test_client()
    response = client.delete('/transactions/1')

    assert response.status_code == 200
    assert b"Transaction with ID 1 has been deleted." in response.data
    