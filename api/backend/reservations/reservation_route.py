from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
 
reservations = Blueprint('reservations', __name__)
 
 
# list incoming reservation requests for his restaurant
@reservations.route('/restaurants/<int:restaurantID>/reservations', methods=['GET'])
def get_restaurant_reservations(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Reservation WHERE RestaurantID = %s ORDER BY date',
                        (restaurantID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_reservations: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# list a customer's own reservations
@reservations.route('/customers/<int:customerID>/reservations', methods=['GET'])
def get_customer_reservations(customerID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Reservation WHERE CustomerID = %s ORDER BY date',
                        (customerID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_customer_reservations: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Request a reservation for a date/time/party size
@reservations.route('/reservations', methods=['POST'])
def create_reservation():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /reservations route')
        data = request.get_json()
 
        for field in ['date', 'partySize', 'customerID', 'restaurantID']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
 
        cursor.execute('''
            INSERT INTO Reservation (date, request, partySize, status, CustomerID, RestaurantID)
            VALUES (%s, %s, %s, 'pending', %s, %s)
        ''', (data['date'], data.get('request'), data['partySize'],
              data['customerID'], data['restaurantID']))
        new_id = cursor.lastrowid
        get_db().commit()
 
        return jsonify({'message': 'Reservation requested', 'resvID': new_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_reservation: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#Accept or decline a pending reservation request
@reservations.route('/reservations/<int:resvID>', methods=['PUT'])
def update_reservation(resvID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /reservations/{resvID} route')
        data = request.get_json()
 
        if 'status' not in data:
            return jsonify({'error': 'Missing required field: status'}), 400
 
        cursor.execute('SELECT * FROM Reservation WHERE resvID = %s', (resvID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Reservation not found'}), 404
 
        cursor.execute('UPDATE Reservation SET status = %s, AppManagerID = %s WHERE resvID = %s',
                        (data['status'], data.get('appManagerID'), resvID))
        get_db().commit()
 
        return jsonify({'message': f'Reservation {resvID} updated to {data["status"]}'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_reservation: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Cancel a reservation
@reservations.route('/reservations/<int:resvID>', methods=['DELETE'])
def cancel_reservation(resvID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /reservations/{resvID} route')
        cursor.execute('SELECT * FROM Reservation WHERE resvID = %s', (resvID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Reservation not found'}), 404
 
        cursor.execute('DELETE FROM Reservation WHERE resvID = %s', (resvID,))
        get_db().commit()
        return jsonify({'message': f'Reservation {resvID} cancelled'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in cancel_reservation: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()