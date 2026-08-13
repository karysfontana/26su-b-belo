from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

admin = Blueprint('admin', __name__)


# 3.1 (Judy): Pending claims queue. Optional ?status= filter.
@admin.route('/claims', methods=['GET'])
def get_claims():
    cursor = get_db().cursor(dictionary=True)
    try:
        status = request.args.get('status')
        query = '''
            SELECT c.claimID, c.status, c.dateSubmitted, c.dateResolved,
                c.restaurantID, r.name AS restaurantName,
                c.managerID, m.firstName AS managerFirst, m.lastName AS managerLast,
                c.adminReviewed
            FROM Claim c
            JOIN Restaurants r ON c.restaurantID = r.RestaurantID
            JOIN Manager m ON c.managerID = m.ManagerID
            WHERE 1=1
        '''
        params = []
        if status:
            query += ' AND c.status = %s'
            params.append(status)
        query += ' ORDER BY c.dateSubmitted ASC'

        cursor.execute(query, params)
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_claims: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Detail view for a single claim
@admin.route('/claims/<int:claimID>', methods=['GET'])
def get_claim(claimID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT c.*, r.name AS restaurantName, r.city, r.state
            FROM Claim c
            JOIN Restaurants r ON c.restaurantID = r.RestaurantID
            WHERE c.claimID = %s
        ''', (claimID,))
        claim = cursor.fetchone()
        if not claim:
            return jsonify({'error': 'Claim not found'}), 404
        return jsonify(claim), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_claim: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 3.1 (Judy): Approve or reject a claim. Also writes an audit log row.
@admin.route('/claims/<int:claimID>', methods=['PUT'])
def resolve_claim(claimID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /claims/{claimID} route')
        data = request.get_json()

        for field in ['status', 'adminID']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if data['status'] not in ('approved', 'rejected'):
            return jsonify({'error': "status must be 'approved' or 'rejected'"}), 400

        cursor.execute('SELECT * FROM Claim WHERE claimID = %s', (claimID,))
        claim = cursor.fetchone()
        if not claim:
            return jsonify({'error': 'Claim not found'}), 404

        cursor.execute('''
            UPDATE Claim
            SET status = %s, dateResolved = NOW(), adminReviewed = %s
            WHERE claimID = %s
        ''', (data['status'], data['adminID'], claimID))

        # look up the restaurant's name so the log reads clearly instead
        # of showing a raw ID
        cursor.execute('SELECT name FROM Restaurants WHERE RestaurantID = %s', (claim['restaurantID'],))
        restaurant = cursor.fetchone()
        restaurant_name = restaurant['name'] if restaurant else f"restaurant #{claim['restaurantID']}"

        cursor.execute('''
            INSERT INTO Log (date, action, adminID)
            VALUES (NOW(), %s, %s)
        ''', (f"Claim {claimID} {data['status']} for {restaurant_name}",
            data['adminID']))

        get_db().commit()
        return jsonify({'message': f"Claim {claimID} {data['status']}"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in resolve_claim: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 3.6 (Judy): Audit log of every admin action, newest first.
@admin.route('/logs', methods=['GET'])
def get_logs():
    cursor = get_db().cursor(dictionary=True)
    try:
        admin_id = request.args.get('adminID')
        query = '''
            SELECT l.logID, l.date, l.action,
                l.adminID, a.firstname, a.lastname
            FROM Log l
            JOIN Admin a ON l.adminID = a.adminID
            WHERE 1=1
        '''
        params = []
        if admin_id:
            query += ' AND l.adminID = %s'
            params.append(admin_id)
        query += ' ORDER BY l.date DESC'

        cursor.execute(query, params)
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_logs: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Record an admin action that happens outside the claim flow
@admin.route('/logs', methods=['POST'])
def create_log():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /logs route')
        data = request.get_json()

        for field in ['action', 'adminID']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        cursor.execute('''
            INSERT INTO Log (date, action, adminID)
            VALUES (NOW(), %s, %s)
        ''', (data['action'], data['adminID']))

        get_db().commit()
        return jsonify({'message': 'Log entry created', 'logID': cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_log: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Admin list, used to populate the "acting as" selector on the admin pages
@admin.route('/admins', methods=['GET'])
def get_admins():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT adminID, firstname, lastname FROM Admin ORDER BY lastname')
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_admins: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()