from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# Create a Blueprint for customer routes
customers = Blueprint("customers", __name__)


# Get all customers
@customers.route("/customers", methods=["GET"])
def get_customers():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT c.customerID, c.firstname, c.lastname, u.status, u.signUpDate
            FROM Customer c
            JOIN User u ON c.userID = u.UserID
        ''')
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_customers: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Get a customer's profile
@customers.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer_profile(customerID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT c.customerID, c.firstname, c.lastname, u.status, u.signUpDate
            FROM Customer c
            JOIN User u ON c.userID = u.UserID
            WHERE c.customerID = %s
        ''', (customerID,))
        theData = cursor.fetchone()
 
        if not theData:
            return jsonify({'error': 'Customer not found'}), 404
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_customer: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

#create a new customer account
@customers.route('/customers', methods=['POST'])
def create_customer():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /customers route')
        data = request.get_json()
 
        for field in ['firstname', 'lastname']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
 
        status = data.get('status', 'active')
 
        cursor.execute('INSERT INTO User (status) VALUES (%s)', (status,))
        new_user_id = cursor.lastrowid
 
        cursor.execute(
            'INSERT INTO Customer (firstname, lastname, userID) VALUES (%s, %s, %s)',
            (data['firstname'], data['lastname'], new_user_id)
        )
        new_customer_id = cursor.lastrowid
 
        get_db().commit()
 
        return jsonify({
            'message': 'Customer account created',
            'customerID': new_customer_id,
            'UserID': new_user_id
        }), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_customer: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Edit customer info
@customers.route('/customers/<int:customerID>', methods=['PUT'])
def update_customer(customerID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /customers/{customerID} route')
        data = request.get_json()
 
        cursor.execute('SELECT * FROM Customer WHERE customerID = %s', (customerID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Customer not found'}), 404
 
        update_fields, params = [], []
        for field in ['firstname', 'lastname']:
            if field in data:
                update_fields.append(f'{field} = %s')
                params.append(data[field])
 
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
 
        params.append(customerID)
        query = f'UPDATE Customer SET {", ".join(update_fields)} WHERE customerID = %s'
        cursor.execute(query, params)
        get_db().commit()
 
        return jsonify({'message': f'Customer {customerID} updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_customer: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Delete an existing customer
@customers.route('/customers/<int:customerID>', methods=['DELETE'])
def delete_customer(customerID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /customers/{customerID} route')
        cursor.execute('SELECT * FROM Customer WHERE customerID = %s', (customerID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Customer not found'}), 404
 
        cursor.execute('DELETE FROM Customer WHERE customerID = %s', (customerID,))
        get_db().commit()
 
        return jsonify({'message': f'Customer {customerID} deleted'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_customer: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()