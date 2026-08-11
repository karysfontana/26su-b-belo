from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

waitlist = Blueprint('waitlist', __name__)


# 2.3 (Bob): Current waitlist for one restaurant.
# ?includeSeated=true returns the full history instead of just who is waiting.
@waitlist.route('/restaurants/<int:restaurantID>/waitlist', methods=['GET'])
def get_restaurant_waitlist(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        include_seated = request.args.get('includeSeated', 'false').lower() == 'true'
        query = '''
            SELECT entryID, firstName, lastName, partySize,
                   arrivalTime, seatedTime, ManagerEdit
            FROM WaitList
            WHERE RestaurantID = %s
        '''
        if not include_seated:
            query += ' AND seatedTime IS NULL'
        query += ' ORDER BY arrivalTime ASC'

        cursor.execute(query, (restaurantID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_waitlist: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Single waitlist entry
@waitlist.route('/waitlist/<int:entryID>', methods=['GET'])
def get_waitlist_entry(entryID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM WaitList WHERE entryID = %s', (entryID,))
        entry = cursor.fetchone()
        if not entry:
            return jsonify({'error': 'Waitlist entry not found'}), 404
        return jsonify(entry), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_waitlist_entry: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 2.3 (Bob): Add a walk-in party to the waitlist
@waitlist.route('/waitlist', methods=['POST'])
def add_to_waitlist():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /waitlist route')
        data = request.get_json()

        for field in ['restaurantID', 'firstName', 'partySize']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        cursor.execute('''
            INSERT INTO WaitList
                (partySize, firstName, lastName, arrivalTime, ManagerEdit, RestaurantID)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        ''', (data['partySize'], data['firstName'], data.get('lastName'),
              data.get('managerID'), data['restaurantID']))

        get_db().commit()
        return jsonify({'message': 'Party added to waitlist',
                        'entryID': cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error in add_to_waitlist: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Seat a waiting party, or correct the party size / name
@waitlist.route('/waitlist/<int:entryID>', methods=['PUT'])
def update_waitlist_entry(entryID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /waitlist/{entryID} route')
        data = request.get_json()

        cursor.execute('SELECT * FROM WaitList WHERE entryID = %s', (entryID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Waitlist entry not found'}), 404

        if data.get('seated'):
            cursor.execute('UPDATE WaitList SET seatedTime = NOW() WHERE entryID = %s',
                           (entryID,))

        if 'partySize' in data:
            cursor.execute('UPDATE WaitList SET partySize = %s WHERE entryID = %s',
                           (data['partySize'], entryID))

        if 'firstName' in data:
            cursor.execute('UPDATE WaitList SET firstName = %s WHERE entryID = %s',
                           (data['firstName'], entryID))

        if 'lastName' in data:
            cursor.execute('UPDATE WaitList SET lastName = %s WHERE entryID = %s',
                           (data['lastName'], entryID))

        if 'managerID' in data:
            cursor.execute('UPDATE WaitList SET ManagerEdit = %s WHERE entryID = %s',
                           (data['managerID'], entryID))

        get_db().commit()
        return jsonify({'message': f'Waitlist entry {entryID} updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_waitlist_entry: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Party left before being seated
@waitlist.route('/waitlist/<int:entryID>', methods=['DELETE'])
def delete_waitlist_entry(entryID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /waitlist/{entryID} route')
        cursor.execute('SELECT * FROM WaitList WHERE entryID = %s', (entryID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Waitlist entry not found'}), 404

        cursor.execute('DELETE FROM WaitList WHERE entryID = %s', (entryID,))
        get_db().commit()
        return jsonify({'message': f'Waitlist entry {entryID} removed'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_waitlist_entry: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()