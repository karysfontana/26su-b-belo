from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
 
reviews = Blueprint('reviews', __name__)
 
 
#Reviews for one restaurant, sorted worst to best
@reviews.route('/restaurants/<int:restaurantID>/reviews', methods=['GET'])
def get_restaurant_reviews(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT rv.reviewID, rv.comment, rv.createdAt, rv.Status,
                   AVG(rt.rate) AS avgRating
            FROM Reviews rv
            JOIN Rating rt ON rv.reviewID = rt.reviewID
            WHERE rv.RestaurantID = %s
            GROUP BY rv.reviewID, rv.comment, rv.createdAt, rv.Status
            ORDER BY avgRating ASC
        ''', (restaurantID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_reviews: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Admin moderation view: all reviews
@reviews.route('/reviews', methods=['GET'])
def get_all_reviews():
    cursor = get_db().cursor(dictionary=True)
    try:
        customer_id = request.args.get('customerID')
        query = 'SELECT * FROM Reviews WHERE 1=1'
        params = []
        if customer_id:
            query += ' AND customerID = %s'
            params.append(customer_id)
        query += ' ORDER BY createdAt DESC'
 
        cursor.execute(query, params)
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_reviews: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# Get one review's ratings breakdown (food/service/vibe)
@reviews.route('/reviews/<int:reviewID>', methods=['GET'])
def get_review(reviewID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Reviews WHERE reviewID = %s', (reviewID,))
        review = cursor.fetchone()
        if not review:
            return jsonify({'error': 'Review not found'}), 404
 
        cursor.execute('SELECT ratingType, rate FROM Rating WHERE reviewID = %s', (reviewID,))
        review['ratings'] = cursor.fetchall()
 
        return jsonify(review), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_review: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
# 1.1 (Peter): Create a review plus its food/service/vibe ratings
@reviews.route('/reviews', methods=['POST'])
def create_review():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /reviews route')
        data = request.get_json()
 
        for field in ['customerID', 'restaurantID', 'comment']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
 
        cursor.execute('''
            INSERT INTO Reviews (comment, createdAt, Status, customerID, RestaurantID)
            VALUES (%s, NOW(), 'active', %s, %s)
        ''', (data['comment'], data['customerID'], data['restaurantID']))
        new_review_id = cursor.lastrowid
 
        for rating_type, rate in data.get('ratings', {}).items():
            cursor.execute(
                'INSERT INTO Rating (reviewID, rate, ratingType) VALUES (%s, %s, %s)',
                (new_review_id, rate, rating_type)
            )
 
        get_db().commit()
        return jsonify({'message': 'Review created', 'reviewID': new_review_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_review: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 

#Revise an existing review's comment and/or its ratings
@reviews.route('/reviews/<int:reviewID>', methods=['PUT'])
def update_review(reviewID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /reviews/{reviewID} route')
        data = request.get_json()
 
        cursor.execute('SELECT * FROM Reviews WHERE reviewID = %s', (reviewID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Review not found'}), 404
 
        if 'comment' in data:
            cursor.execute('UPDATE Reviews SET comment = %s WHERE reviewID = %s',
                            (data['comment'], reviewID))
 
        for rating_type, rate in data.get('ratings', {}).items():
            cursor.execute(
                'UPDATE Rating SET rate = %s WHERE reviewID = %s AND ratingType = %s',
                (rate, reviewID, rating_type)
            )
 
        get_db().commit()
        return jsonify({'message': f'Review {reviewID} updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_review: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
 
 
#Delete own review (admin and customer)
@reviews.route('/reviews/<int:reviewID>', methods=['DELETE'])
def delete_review(reviewID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /reviews/{reviewID} route')
        cursor.execute('SELECT * FROM Reviews WHERE reviewID = %s', (reviewID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Review not found'}), 404
 
        cursor.execute('DELETE FROM Reviews WHERE reviewID = %s', (reviewID,))
        get_db().commit()
        return jsonify({'message': f'Review {reviewID} deleted'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_review: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

# Reviews written by people this user follows 
@reviews.route('/reviews/friends/<int:userID>', methods=['GET'])
def get_friends_reviews(userID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT rv.*, c.firstname, c.lastname, r.name AS restaurantName
            FROM Follows f
            JOIN Customer c ON f.followingID = c.userID
            JOIN Reviews rv ON c.customerID = rv.customerID
            JOIN Restaurants r ON rv.RestaurantID = r.RestaurantID
            WHERE f.followerID = %s AND rv.Status = 'active'
            ORDER BY rv.createdAt DESC
        ''', (userID,))
        theData = cursor.fetchall()

        for rv in theData:
            cursor.execute(
                'SELECT ratingType, rate FROM Rating WHERE reviewID = %s',
                (rv['reviewID'],)
            )
            rv['ratings'] = cursor.fetchall()

        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_friends_reviews: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()