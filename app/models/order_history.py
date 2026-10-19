from flask import current_app as app
from datetime import datetime

class OrderHistory:
    def __init__(self, order_id, buyer_key, product_key, seller_key, seller_name, cat_name, product_name, 
                 product_price, order_quantity, is_fulfilled, order_time, prod_review_id, user_review_id):
        self.order_id = order_id
        self.buyer_key = buyer_key
        self.product_key = product_key
        self.seller_key = seller_key
        self.seller_name = seller_name
        self.category = cat_name
        self.product_name = product_name
        self.price = product_price
        self.quantity = order_quantity
        self.is_fulfilled = 'Delivered' if is_fulfilled else 'Ordered'
        self.order_time = order_time
        self.order_date = self.parse_date(order_time)
        self.time_of_order = self.parse_time(order_time)
        self.prod_review_id = prod_review_id
        self.user_review_id = user_review_id

    def parse_date(self, order_time):
        return order_time.date()
    
    def parse_time(self, order_time):
        return order_time.time()
    
    @staticmethod
    def get_by_order_id(order_id):
        rows = app.db.execute('''
SELECT order_id, buyer_key, product_key, order_time
FROM OrderHistory
WHERE order_id = :order_id
''',
                              order_id=order_id)
        return OrderHistory(*(rows[0])) if rows else None

    @staticmethod
    def get_by_user_id(id, cur_page, per_page):
        rows = app.db.execute('''
            SELECT OrderHistory.order_id, OrderHistory.buyer_key, OrderHistory.product_key, OrderHistory.seller_key, 
            Users.firstname, Product_Category.cat_name, Products.product_name, Products.product_price, 
            OrderHistory.order_quantity, OrderHistory.is_fulfilled, OrderHistory.order_time, OrderHistory.prod_review_id, OrderHistory.user_review_id
            FROM OrderHistory
            JOIN Products ON OrderHistory.product_key = Products.product_key
            JOIN Product_Category ON Products.cat_key = Product_Category.cat_key
            JOIN Users ON OrderHistory.seller_key = Users.id
            WHERE OrderHistory.buyer_key = :id
            ORDER BY OrderHistory.order_time DESC                              
            LIMIT 10
            OFFSET :offset;                                                                                                                                                  
            ''',
                            id=id,
                            offset = (cur_page-1)*per_page)
        
        res = [OrderHistory(*row) for row in rows] if rows else []

        tmp = app.db.execute('''
            SELECT COUNT(*)
            FROM OrderHistory
            WHERE OrderHistory.buyer_key = :id;                                                                                                                                                  
            ''',
                            id = id)
        total_pages = tmp[0][0]

        incomplete = True if total_pages % per_page != 0 else False
        total_pages = total_pages // per_page
        total_pages = total_pages + 1 if incomplete else total_pages

        return res, total_pages

    @staticmethod
    def get_all_by_uid_since(buyer_key, since):
        rows = app.db.execute('''
SELECT order_id, buyer_key, product_key, order_time
FROM OrderHistory
WHERE buyer_key = :buyer_key
AND order_time >= :since
ORDER BY order_time DESC
''',
                              buyer_key=buyer_key,
                              since=since)
        return [OrderHistory(*row) for row in rows]
    
    @staticmethod
    def get_product_seller_from_order(order_id):
        rows = app.db.execute('''
SELECT product_key, seller_key
FROM OrderHistory
WHERE order_id = :order_id
''',
                              order_id=order_id)
        return OrderHistory(*(rows[0])) if rows else None

    @staticmethod
    def add_order_history(buyer_key, product_key, seller_key, quantity):
        """Add a new order to the OrderHistory table."""
        try:
            result = app.db.execute('''
                INSERT INTO OrderHistory (buyer_key, seller_key, product_key, order_quantity, is_fulfilled)
                VALUES (:buyer_key, :seller_key, :product_key, :quantity, FALSE)
                RETURNING order_id
                ''',
                buyer_key=buyer_key,
                seller_key=seller_key,
                product_key=product_key,
                quantity=quantity
            )
            order_id = result.fetchone()[0]
            return order_id
        except Exception as e:
            print(f"Error inserting order history: {str(e)}")
            return None
