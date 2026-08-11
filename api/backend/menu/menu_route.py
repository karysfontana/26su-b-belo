from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

menu = Blueprint('menu', __name__)


# Full menu for one restaurant (resolves Restaurants.MenuID for the caller)
@menu.route('/restaurants/<int:restaurantID>/menu', methods=['GET'])
def get_restaurant_menu(restaurantID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT MenuID FROM Restaurants WHERE RestaurantID = %s',
                       (restaurantID,))
        restaurant = cursor.fetchone()
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404

        cursor.execute('''
            SELECT itemID, menuID, name, price
            FROM Menu_Item
            WHERE menuID = %s
            ORDER BY name
        ''', (restaurant['MenuID'],))

        return jsonify({'menuID': restaurant['MenuID'],
                        'items': cursor.fetchall()}), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_menu: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Items on a menu, addressed by menuID directly
@menu.route('/menus/<int:menuID>/items', methods=['GET'])
def get_menu_items(menuID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT itemID, menuID, name, price
            FROM Menu_Item
            WHERE menuID = %s
            ORDER BY name
        ''', (menuID,))
        theData = cursor.fetchall()
        return jsonify(theData), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_menu_items: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# One item
@menu.route('/menus/<int:menuID>/items/<int:itemID>', methods=['GET'])
def get_menu_item(menuID, itemID):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM Menu_Item WHERE menuID = %s AND itemID = %s',
                       (menuID, itemID))
        item = cursor.fetchone()
        if not item:
            return jsonify({'error': 'Menu item not found'}), 404
        return jsonify(item), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_menu_item: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 2.5 (Bob): Add a dish. Menu_Item has a composite PK and itemID is not
# auto-increment, so the next itemID is derived per menu.
@menu.route('/menus/<int:menuID>/items', methods=['POST'])
def create_menu_item(menuID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /menus/{menuID}/items route')
        data = request.get_json()

        for field in ['name', 'price']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        cursor.execute('SELECT menuID FROM Menu WHERE menuID = %s', (menuID,))
        if not cursor.fetchone():
            return jsonify({'error': 'Menu not found'}), 404

        cursor.execute(
            'SELECT COALESCE(MAX(itemID), 0) + 1 AS nextID FROM Menu_Item WHERE menuID = %s',
            (menuID,))
        next_id = cursor.fetchone()['nextID']

        cursor.execute('''
            INSERT INTO Menu_Item (itemID, menuID, name, price)
            VALUES (%s, %s, %s, %s)
        ''', (next_id, menuID, data['name'], data['price']))

        get_db().commit()
        return jsonify({'message': 'Menu item created',
                        'itemID': next_id, 'menuID': menuID}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_menu_item: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Rename a dish or change its price
@menu.route('/menus/<int:menuID>/items/<int:itemID>', methods=['PUT'])
def update_menu_item(menuID, itemID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /menus/{menuID}/items/{itemID} route')
        data = request.get_json()

        cursor.execute('SELECT * FROM Menu_Item WHERE menuID = %s AND itemID = %s',
                       (menuID, itemID))
        if not cursor.fetchone():
            return jsonify({'error': 'Menu item not found'}), 404

        if 'name' in data:
            cursor.execute(
                'UPDATE Menu_Item SET name = %s WHERE menuID = %s AND itemID = %s',
                (data['name'], menuID, itemID))

        if 'price' in data:
            cursor.execute(
                'UPDATE Menu_Item SET price = %s WHERE menuID = %s AND itemID = %s',
                (data['price'], menuID, itemID))

        get_db().commit()
        return jsonify({'message': f'Menu item {itemID} updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_menu_item: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 2.5 (Bob): Take a dish off the menu
@menu.route('/menus/<int:menuID>/items/<int:itemID>', methods=['DELETE'])
def delete_menu_item(menuID, itemID):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /menus/{menuID}/items/{itemID} route')
        cursor.execute('SELECT * FROM Menu_Item WHERE menuID = %s AND itemID = %s',
                       (menuID, itemID))
        if not cursor.fetchone():
            return jsonify({'error': 'Menu item not found'}), 404

        cursor.execute('DELETE FROM Menu_Item WHERE menuID = %s AND itemID = %s',
                       (menuID, itemID))
        get_db().commit()
        return jsonify({'message': f'Menu item {itemID} deleted'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_menu_item: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()