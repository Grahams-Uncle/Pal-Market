from flask import current_app as app
from flask import flash

class Cart:
    def __init__(self, cart_item_id, buyer_key, product_key, seller_key, quantity, price, total_price, added_to_cart_time):
        self.cart_item_id = cart_item_id
        self.buyer_key = buyer_key
        self.product_key = product_key
        self.seller_key = seller_key
        self.quantity = quantity
        self.price = price
        self.total_price = total_price
        self.added_to_cart_time = added_to_cart_time

    @staticmethod
    def get_cart_items_by_user_id(user_id):
        
        rows = app.db.execute('''
            SELECT Cart.cart_item_id, Cart.buyer_key, Cart.product_key, Cart.seller_key, 
                Cart.quantity, Cart.price, Cart.total_price, Cart.added_to_cart_time,
                Products.product_name, Products.product_image
            FROM Cart
            JOIN Products ON Cart.product_key = Products.product_key AND Cart.seller_key = Products.seller_key
            WHERE Cart.buyer_key = :user_id
            ORDER BY Cart.added_to_cart_time DESC
            ''',
            user_id=user_id)

        cart_items = [{
            'cart_item_id': row[0],
            'buyer_key': row[1],
            'product_key': row[2],
            'seller_key': row[3],
            'quantity': row[4],
            'price': row[5],
            'total_price': row[6],
            'added_to_cart_time': row[7],
            'product_name': row[8],
            'product_image': row[9]
        } for row in rows]

        latest_prices = {}
        for item in cart_items:
            if item['product_name'] not in latest_prices:
                latest_prices[item['product_name']] = item['price']

        for item in cart_items:
            if item['price'] != latest_prices[item['product_name']]:
                update_price_query = '''
                    UPDATE Cart
                    SET price = :new_price, total_price = quantity * :new_price
                    WHERE cart_item_id = :cart_item_id
                '''
                app.db.execute(update_price_query, new_price=latest_prices[item['product_name']], cart_item_id=item['cart_item_id'])

        updated_rows = app.db.execute('''
            SELECT Cart.cart_item_id, Cart.buyer_key, Cart.product_key, Cart.seller_key, 
                Cart.quantity, Cart.price, Cart.total_price, Cart.added_to_cart_time,
                Products.product_name, Products.product_image
            FROM Cart
            JOIN Products ON Cart.product_key = Products.product_key AND Cart.seller_key = Products.seller_key
            WHERE Cart.buyer_key = :user_id
            ORDER BY Cart.added_to_cart_time DESC
            ''',
            user_id=user_id)

        return [{
            'cart_item_id': row[0],
            'buyer_key': row[1],
            'product_key': row[2],
            'seller_key': row[3],
            'quantity': row[4],
            'price': row[5],
            'total_price': row[6],
            'added_to_cart_time': row[7],
            'product_name': row[8],
            'product_image': row[9]
        } for row in updated_rows]


    @staticmethod
    def get_cart_item(cart_item_id,buyer_key):
        query = '''
            SELECT * FROM Cart WHERE cart_item_id = :cart_item_id AND buyer_key = :buyer_key
        '''
        rows = app.db.execute(query, cart_item_id = cart_item_id, buyer_key = buyer_key)
        return [Cart(*row) for row in rows]


    @staticmethod
    def update_cart(cart_item_id, buyer_key, quantity, price):
        inventory_check_query = '''
            SELECT I.quantity
            FROM Inventory I
            JOIN Cart C ON I.product_key = C.product_key AND I.seller_key = C.seller_key
            WHERE C.cart_item_id = :cart_item_id
        '''
        result = app.db.execute(inventory_check_query, cart_item_id=cart_item_id)
        if not result:
            flash('No inventory record found.', 'error')
            return False

        available_inventory = result[0][0]
        if quantity > available_inventory:
            flash('Requested quantity exceeds available inventory.', 'error')
            return False

        total_price = price * quantity
        update_query = '''
            UPDATE Cart
            SET quantity = :quantity, total_price = :total_price
            WHERE cart_item_id = :cart_item_id AND buyer_key = :buyer_key
        '''
        app.db.execute(update_query, cart_item_id=cart_item_id, buyer_key=buyer_key, quantity=quantity, total_price=total_price)
        flash('Cart updated successfully!', 'success')
        return True

    @staticmethod
    def remove_from_cart(cart_item_id, buyer_key):
        query = '''
            DELETE FROM Cart WHERE cart_item_id = :cart_item_id AND buyer_key = :buyer_key
        '''
        app.db.execute(query, cart_item_id=cart_item_id, buyer_key=buyer_key)

    @staticmethod
    def empty_cart(buyer_id):
        query = '''
            DELETE FROM Cart WHERE buyer_key = :buyer_id
        '''
        app.db.execute(query, buyer_id=buyer_id)





