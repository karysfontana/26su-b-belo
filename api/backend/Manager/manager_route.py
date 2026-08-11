from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
 
managers = Blueprint('managers', __name__)
 
 
# List all managers
@managers.route('/managers', methods=['GET'])
def get_managers():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT m.ManagerID, m.firstname, m.lastname, u.status
            FROM Manager m
            JOIN User u ON m.userID = u.UserID
        ''')
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_managers: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#------------------------------------------------------------
# Get one manager's profile
@managers.route('/managers/<int:managerID>', methods=['GET'])
def get_manager(managerID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT m.ManagerID, m.firstname, m.lastname, u.status
            FROM Manager m
            JOIN User u ON m.userID = u.UserID
            WHERE m.ManagerID = %s
        ''', (managerID,))
        theData = cursor.fetchone()
 
        if not theData:
            return jsonify({'error': 'Manager not found'}), 404
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_manager: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#------------------------------------------------------------
# List every restaurant this manager owns/manages
@managers.route('/managers/<int:managerID>/restaurants', methods=['GET'])
def get_manager_restaurants(managerID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Restaurants WHERE ManagerID = %s', (managerID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_manager_restaurants: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#------------------------------------------------------------
# Edit manager info
# Body: { "firstname": "...", "lastname": "..." }
@managers.route('/managers/<int:managerID>', methods=['PUT'])
def update_manager(managerID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /managers/{managerID} route')
        data = request.get_json()
 
        cursor.execute('SELECT * FROM Manager WHERE ManagerID = %s', (managerID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Manager not found'}), 404
 
        update_fields, params = [], []
        for field in ['firstname', 'lastname']:
            if field in data:
                update_fields.append(f'{field} = %s')
                params.append(data[field])
 
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
 
        params.append(managerID)
        query = f'UPDATE Manager SET {", ".join(update_fields)} WHERE ManagerID = %s'
        cursor.execute(query, params)
        get_db().commit()
 
        return jsonify({'message': f'Manager {managerID} updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_manager: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 