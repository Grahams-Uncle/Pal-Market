from flask import current_app as app
from sqlalchemy import text
from collections import Counter

class SaleHistory:
    def __init__(self, id, buyer_key, product_key, lastname, firstname, street_num, street_name, state, state_id, zipcode,\
                 product_name, product_price, order_quantity, is_fulfilled, sale_time, fulfill_time, review_rating):
        self.id = id
        self.buyer_key = buyer_key
        self.product_key = product_key
        self.buyer_name = firstname + " " + lastname
        self.buyer_address = str(street_num) + " " + street_name
        self.state = state
        self.state_id = state_id
        self.zipcode = zipcode
        self.prod_name = product_name
        self.prod_price = product_price
        self.sale_qty = order_quantity
        self.is_fulfilled = 'Delivered' if is_fulfilled else 'Ordered'
        self.sale_time = sale_time
        self.fulfill_time = fulfill_time
        self.review_rating = review_rating
    
    @staticmethod
    def get_unfulfilled(id, sort="date", order="desc", search_term=None, search_criteria=None, min_price=None, max_price=None, start_date=None, end_date=None, selected_state=None, page=1, per_page=25):
        offset = (page - 1) * per_page
        query = ''' SELECT OrderHistory.order_id, OrderHistory.buyer_key, OrderHistory.product_key,
                    buyer.lastname, buyer.firstname, Address_Table.street_num, Address_Table.street_name, Zipcode.state, Zipcode.state_id, Zipcode.zipcode,
                    Products.product_name, Products.product_price,
                    OrderHistory.order_quantity, OrderHistory.is_fulfilled, OrderHistory.order_time, OrderHistory.fulfillment_time,
                    ProductReviews.review_rating
                FROM OrderHistory
                JOIN Products ON OrderHistory.product_key = Products.product_key
                JOIN Product_Category ON Products.cat_key = Product_Category.cat_key
                JOIN Users seller ON OrderHistory.seller_key = seller.id
                JOIN Users buyer ON OrderHistory.buyer_key = buyer.id
                JOIN Address_Table ON buyer.user_ship_address = Address_Table.address_key
                JOIN Zipcode ON Zipcode.zipcode = Address_Table.zipcode
                LEFT OUTER JOIN ProductReviews ON
                    ProductReviews.product_key = OrderHistory.product_key
                    AND ProductReviews.seller_key = OrderHistory.seller_key
                    AND ProductReviews.person_reviewing_id = OrderHistory.buyer_key
                    AND ProductReviews.prod_review_id = OrderHistory.prod_review_id
                WHERE OrderHistory.seller_key = :id AND OrderHistory.is_fulfilled = 'f' '''

        query_params = {"id": id, "limit": per_page, "offset": offset}

        if search_term:
            # Add the search criteria to the query
            query += f" AND {search_criteria} = :search_term"
            query_params["search_term"] = search_term
        
        if selected_state:
            query += f" AND Zipcode.state = :selected_state"
            query_params["selected_state"] = selected_state
        if min_price:
            query += f" AND Products.product_price > :min_price"
            query_params["min_price"] = min_price
        
        if max_price:
            query += f" AND Products.product_price < :max_price"
            query_params["max_price"] = max_price
        
        query += " AND DATE(OrderHistory.order_time) BETWEEN COALESCE(:start_date, '1000-01-01'::DATE) AND COALESCE(:end_date, '9999-12-31'::DATE)"
        query_params["start_date"] = start_date
        query_params["end_date"] = end_date
        query_map = {
                     "pname":'ORDER BY Products.product_name ',
                     "bname":'ORDER BY buyer.firstname ',
                     "date":'ORDER BY OrderHistory.order_time ',
                     "price":'ORDER BY Products.product_price '
                    }

        query += query_map[sort] + order.upper()
        query +=''' LIMIT :limit OFFSET :offset;'''

        # Execute the query with the provided parameters
        with app.db.engine.begin() as conn:
            rows = conn.execute(text(query), query_params)
        
        # Return the results as SaleHistory objects
        return [SaleHistory(*row) for row in rows] if rows else None
    
    @staticmethod
    def count_unfulfilled(seller_id, search_term=None, search_criteria=None,min_price=None, max_price=None, start_date=None, end_date=None, selected_state=None):
        # Count the total number of unfulfilled orders for `seller_id`

        query = ''' SELECT COALESCE(COUNT(DISTINCT order_id))
        FROM OrderHistory
        JOIN Products ON OrderHistory.product_key = Products.product_key
        JOIN Product_Category ON Products.cat_key = Product_Category.cat_key
        JOIN Users seller ON OrderHistory.seller_key = seller.id
        JOIN Users buyer ON OrderHistory.buyer_key = buyer.id
        JOIN Address_Table ON buyer.user_ship_address = Address_Table.address_key
        JOIN Zipcode ON Zipcode.zipcode = Address_Table.zipcode
        LEFT OUTER JOIN ProductReviews ON
            ProductReviews.product_key = OrderHistory.product_key
            AND ProductReviews.seller_key = OrderHistory.seller_key
            AND ProductReviews.person_reviewing_id = OrderHistory.buyer_key
            AND ProductReviews.prod_review_id = OrderHistory.prod_review_id
        WHERE OrderHistory.seller_key = :id AND OrderHistory.is_fulfilled = 'f' '''

        query_params = {"id": seller_id}
        if search_term:
            # Add the search criteria to the query
            query += f" AND {search_criteria} = :search_term"
            query_params["search_term"] = search_term
        if selected_state:
            query += f" AND Zipcode.state = :selected_state"
            query_params["selected_state"] = selected_state
        if min_price:
            query += f" AND Products.product_price > :min_price"
            query_params["min_price"] = min_price
        
        if max_price:
            query += f" AND Products.product_price < :max_price"
            query_params["max_price"] = max_price
        query += " AND DATE(OrderHistory.order_time) BETWEEN COALESCE(:start_date, '1000-01-01'::DATE) AND COALESCE(:end_date, '9999-12-31'::DATE)"
        query_params["start_date"] = start_date
        query_params["end_date"] = end_date
        with app.db.engine.begin() as conn:
            count = conn.execute(text(query), query_params)

        return int(count.fetchone()[0])
    
    @staticmethod
    def get_fulfilled(id, sort="date", order="desc", search_term=None, search_criteria=None, min_price=None, max_price=None, start_date=None, end_date=None, selected_state=None, page=1, per_page=25):
        offset = (page - 1) * per_page
        query = ''' SELECT OrderHistory.order_id, OrderHistory.buyer_key, OrderHistory.product_key,
                    buyer.lastname, buyer.firstname, Address_Table.street_num, Address_Table.street_name, Zipcode.state, Zipcode.state_id, Zipcode.zipcode,
                    Products.product_name, Products.product_price,
                    OrderHistory.order_quantity, OrderHistory.is_fulfilled, OrderHistory.order_time, OrderHistory.fulfillment_time,
                    ProductReviews.review_rating
                FROM OrderHistory
                JOIN Products ON OrderHistory.product_key = Products.product_key
                JOIN Product_Category ON Products.cat_key = Product_Category.cat_key
                JOIN Users seller ON OrderHistory.seller_key = seller.id
                JOIN Users buyer ON OrderHistory.buyer_key = buyer.id
                JOIN Address_Table ON buyer.user_ship_address = Address_Table.address_key
                JOIN Zipcode ON Zipcode.zipcode = Address_Table.zipcode
                LEFT OUTER JOIN ProductReviews ON
                    ProductReviews.product_key = OrderHistory.product_key
                    AND ProductReviews.seller_key = OrderHistory.seller_key
                    AND ProductReviews.person_reviewing_id = OrderHistory.buyer_key
                    AND ProductReviews.prod_review_id = OrderHistory.prod_review_id
                WHERE OrderHistory.seller_key = :id AND OrderHistory.is_fulfilled = 't' '''

        query_params = {"id": id, "limit": per_page, "offset": offset}

        if search_term:
            # Add the search criteria to the query
            query += f" AND {search_criteria} = :search_term"
            query_params["search_term"] = search_term

        if selected_state:
            query += f" AND Zipcode.state = :selected_state"
            query_params["selected_state"] = selected_state
        
        if min_price:
            query += f" AND Products.product_price > :min_price"
            query_params["min_price"] = min_price
        
        if max_price:
            query += f" AND Products.product_price < :max_price"
            query_params["max_price"] = max_price
        
        query += " AND DATE(OrderHistory.order_time) BETWEEN COALESCE(:start_date, '1000-01-01'::DATE) AND COALESCE(:end_date, '9999-12-31'::DATE)"
        query_params["start_date"] = start_date
        query_params["end_date"] = end_date
        query_map = {
                     "pname":'ORDER BY Products.product_name ',
                     "bname":'ORDER BY buyer.firstname ',
                     "date":'ORDER BY OrderHistory.order_time ',
                     "price":'ORDER BY Products.product_price '
                    }

        query += query_map[sort] + order.upper()
        query +=''' LIMIT :limit OFFSET :offset;'''
        # Execute the query with the provided parameters
        with app.db.engine.begin() as conn:
            rows = conn.execute(text(query), query_params)
        
        # Return the results as SaleHistory objects
        return [SaleHistory(*row) for row in rows] if rows else None
    
    @staticmethod
    def count_fulfilled(seller_id, search_term=None, search_criteria=None,min_price=None, max_price=None, start_date=None, end_date=None, selected_state=None):
        # Count the total number of fulfilled orders for `seller_id`
        query = ''' SELECT COALESCE(COUNT(DISTINCT order_id),1)
        FROM OrderHistory
        JOIN Products ON OrderHistory.product_key = Products.product_key
        JOIN Product_Category ON Products.cat_key = Product_Category.cat_key
        JOIN Users seller ON OrderHistory.seller_key = seller.id
        JOIN Users buyer ON OrderHistory.buyer_key = buyer.id
        JOIN Address_Table ON buyer.user_ship_address = Address_Table.address_key
        JOIN Zipcode ON Zipcode.zipcode = Address_Table.zipcode
        LEFT OUTER JOIN ProductReviews ON
            ProductReviews.product_key = OrderHistory.product_key
            AND ProductReviews.seller_key = OrderHistory.seller_key
            AND ProductReviews.person_reviewing_id = OrderHistory.buyer_key
            AND ProductReviews.prod_review_id = OrderHistory.prod_review_id
        WHERE OrderHistory.seller_key = :id AND OrderHistory.is_fulfilled = 't' '''

        query_params = {"id": seller_id}
        if search_term:
            # Add the search criteria to the query
            query += f" AND {search_criteria} = :search_term"
            query_params["search_term"] = search_term
        if selected_state:
            query += f" AND Zipcode.state = :selected_state"
            query_params["selected_state"] = selected_state
        if min_price:
            query += f" AND Products.product_price > :min_price"
            query_params["min_price"] = min_price
        
        if max_price:
            query += f" AND Products.product_price < :max_price"
            query_params["max_price"] = max_price
        query += " AND DATE(OrderHistory.order_time) BETWEEN COALESCE(:start_date, '1000-01-01'::DATE) AND COALESCE(:end_date, '9999-12-31'::DATE)"
        query_params["start_date"] = start_date
        query_params["end_date"] = end_date
        with app.db.engine.begin() as conn:
            count = conn.execute(text(query), query_params)

        return int(count.fetchone()[0])
    
    @staticmethod
    def get_product_trend( seller_id, product_id):
        query = '''
            SELECT
                to_char(month, 'YYYY-MM') AS month,
                COALESCE(SUM(order_quantity), 0) AS total_quantity
            FROM generate_series(
                DATE_TRUNC('month', NOW()) - INTERVAL '11 months',
                DATE_TRUNC('month', NOW()),
                INTERVAL '1 month'
            ) AS month
            LEFT OUTER JOIN OrderHistory ON DATE_TRUNC('month', order_time) = month
                AND product_key = :product_key AND seller_key = :seller_key
            GROUP BY month
            ORDER BY month;
        '''
        with app.db.engine.begin() as conn:
            trends = conn.execute(text(query), {"seller_key":seller_id, "product_key":product_id})
        months = []
        quantities = []

        for row in trends:
            months.append(row[0])
            quantities.append(row[1])

        return {'months': months, 'quantities': quantities}

    @staticmethod
    def get_top_products(seller_id):
        # Query the database to retrieve the top 10 selling products for the seller
        query = '''
            SELECT p.seller_key, p.product_key, p.product_name, p.product_image, SUM(oh.order_quantity) AS total_quantity
            FROM Products p
                 JOIN OrderHistory oh ON p.product_key = oh.product_key AND p.seller_key = oh.seller_key
            WHERE p.seller_key = :seller_id
            GROUP BY p.seller_key, p.product_key, p.product_name, p.product_image
            ORDER BY total_quantity DESC
            LIMIT 10
        '''
        with app.db.engine.begin() as conn:
            top_selling_products = conn.execute(text(query), {'seller_id': seller_id}).fetchall()

        return top_selling_products
    
    @staticmethod
    def get_buyer_ratings(seller_id):
        query = ''' WITH User_Ratings AS (
                        SELECT id, COALESCE(AVG(review_rating), 5.0) AS rating
                        FROM Users
                        LEFT JOIN UserReviews ON id = person_key
                        GROUP BY id
                    )
                    SELECT DISTINCT User_Ratings.id, User_Ratings.rating
                    FROM OrderHistory JOIN User_Ratings ON OrderHistory.buyer_key = User_Ratings.id
                    WHERE OrderHistory.seller_key = :seller_key
                '''
        with app.db.engine.begin() as conn:
            buyer_ratings = conn.execute(text(query), {'seller_key': seller_id}).fetchall()
        all_ratings = [round(x * 0.01, 2) for x in range(0, 501)]
        counts = Counter([round(float(i[1]),2) for i in buyer_ratings])
        rating_counts = {rating: counts.get(rating, 0) for rating in all_ratings}
        ratings = {"ratings": list(rating_counts.keys()), "counts": list(rating_counts.values())}
        return ratings