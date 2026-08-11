from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
 
users = Blueprint('users', __name__)
 
 
# List all user accounts (admin support)
@users.route('/users', methods=['GET'])
def get_users():
    cursor = get_db().cursor(dictionary=True)
    try:
        status = request.args.get('status')
        query = 'SELECT * FROM User WHERE 1=1'
        params = []
        if status:
            query += ' AND status = %s'
            params.append(status)
 
        cursor.execute(query, params)
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_users: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Get one account's status
@users.route('/users/<int:userID>', methods=['GET'])
def get_user(userID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM User WHERE UserID = %s', (userID,))
        theData = cursor.fetchone()
 
        if not theData:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_user: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# List who a user follows
@users.route('/users/<int:userID>/follows', methods=['GET'])
def get_follows(userID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT u.UserID, u.status
            FROM Follows f
            JOIN User u ON f.followingID = u.UserID
            WHERE f.followerID = %s
        ''', (userID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_follows: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#Follow another user
@users.route('/users/<int:userID>/follows', methods=['POST'])
def add_follow(userID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /users/{userID}/follows route')
        data = request.get_json()
 
        if 'followingID' not in data:
            return jsonify({'error': 'Missing required field: followingID'}), 400
 
        cursor.execute('SELECT * FROM User WHERE UserID = %s', (data['followingID'],))
        if not cursor.fetchone():
            return jsonify({'error': 'User to follow not found'}), 404
 
        cursor.execute('INSERT INTO Follows (followerID, followingID) VALUES (%s, %s)',
                        (userID, data['followingID']))
        get_db().commit()
 
        return jsonify({'message': 'Now following'}), 201
    except Error as e:
        current_app.logger.error(f'Database error in add_follow: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#Suspend (or reinstate) an account
@users.route('/users/<int:userID>', methods=['PUT'])
def update_user_status(userID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /users/{userID} route')
        data = request.get_json()
 
        if 'status' not in data:
            return jsonify({'error': 'Missing required field: status'}), 400
 
        cursor.execute('SELECT * FROM User WHERE UserID = %s', (userID,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404
 
        cursor.execute('UPDATE User SET status = %s, flaggedBy = %s WHERE UserID = %s',
                        (data['status'], data.get('flaggedBy'), userID))
        get_db().commit()
 
        return jsonify({'message': f'User {userID} status set to {data["status"]}'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_user_status: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Permanently remove an account
@users.route('/users/<int:userID>', methods=['DELETE'])
def delete_user(userID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /users/{userID} route')
        cursor.execute('SELECT * FROM User WHERE UserID = %s', (userID,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404
 
        cursor.execute('DELETE FROM User WHERE UserID = %s', (userID,))
        get_db().commit()
 
        return jsonify({'message': f'User {userID} deleted'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_user: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()