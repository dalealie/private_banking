import pytest
from app import app

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
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
    mock_db.fetchall.return_value = [(1, 'Alice')]
    client = app.test_client()
    response = client.get('/employees')
    assert response.status_code == 200
    assert b"Alice" in response.data

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
    assert b"John Doe" in response.data


def test_add_employee_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/employees', json={})
    assert response.status_code == 400
    assert b"Employee ID is required" in response.data

def test_add_employee_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/employees', json={'employee_ID': 1})
    assert response.status_code == 201
    assert b"Employee with ID 1 added successfully" in response.data


def test_update_employee_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/employees/1', json={})
    assert response.status_code == 400
    assert b"No updates provided for the employee" in response.data

def test_update_employee_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.put('/employees/999', json={'Name': 'Updated Name'})
    assert response.status_code == 404
    assert b"Employee not found" in response.data


def test_delete_employee_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.delete('/employees/999')
    assert response.status_code == 404
    assert b"Employee not found" in response.data

def test_delete_employee_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.delete('/employees/1')
    assert response.status_code == 200
    assert b"Employee with ID 1 has been deleted." in response.data

if __name__ == "__main__":
    pytest.main()