from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

seatingchart = Blueprint("seatingchart", __name__)


#View seating charts for a restaurant, optionally filtered by date
@seatingchart.route('/restaurants/<int:restaurantID>/seatingcharts', methods=['GET'])
def get_restaurant_seatingcharts(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        date_filter = request.args.get('date')
        query = 'SELECT * FROM SeatingChart WHERE RestaurantID = %s'
        params = [restaurantID]
        if date_filter:
            query += ' AND date = %s'
            params.append(date_filter)
        query += ' ORDER BY date DESC'

        cursor.execute(query, params)
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_seatingcharts: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Get one seating chart's details
@seatingchart.route('/seatingcharts/<int:chartID>', methods=['GET'])
def get_seatingchart(chartID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM SeatingChart WHERE chartID = %s', (chartID,))
        chart = cursor.fetchone()
        if not chart:
            return jsonify({'error': 'Seating chart not found'}), 404
        return jsonify(chart), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_seatingchart: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Create a seating chart for a restaurant/date
@seatingchart.route('/seatingcharts', methods=['POST'])
def create_seatingchart():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /seatingcharts route')
        data = request.get_json()

        for field in ['restaurantID', 'date', 'totalCovers']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        open_table = data.get('openTable', data['totalCovers'])

        cursor.execute('''
            INSERT INTO SeatingChart (totalCovers, date, openTable, RestaurantID)
            VALUES (%s, %s, %s, %s)
        ''', (data['totalCovers'], data['date'], open_table, data['restaurantID']))
        new_id = cursor.lastrowid
        get_db().commit()

        return jsonify({'message': 'Seating chart created', 'chartID': new_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_seatingchart: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Set how many tables are bookable for a given chart
@seatingchart.route('/seatingcharts/<int:chartID>', methods=['PUT'])
def update_seatingchart(chartID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /seatingcharts/{chartID} route')
        data = request.get_json()

        cursor.execute('SELECT * FROM SeatingChart WHERE chartID = %s', (chartID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Seating chart not found'}), 404

        update_fields, params = [], []
        for field in ['openTable', 'totalCovers']:
            if field in data:
                update_fields.append(f'{field} = %s')
                params.append(data[field])

        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400

        params.append(chartID)
        query = f'UPDATE SeatingChart SET {", ".join(update_fields)} WHERE chartID = %s'
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({'message': f'Seating chart {chartID} updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_seatingchart: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Remove a seating chart
@seatingchart.route('/seatingcharts/<int:chartID>', methods=['DELETE'])
def delete_seatingchart(chartID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /seatingcharts/{chartID} route')
        cursor.execute('SELECT * FROM SeatingChart WHERE chartID = %s', (chartID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Seating chart not found'}), 404

        cursor.execute('DELETE FROM SeatingChart WHERE chartID = %s', (chartID,))
        get_db().commit()

        return jsonify({'message': f'Seating chart {chartID} deleted'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_seatingchart: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()