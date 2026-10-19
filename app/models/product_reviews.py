from flask import current_app as app
from sqlalchemy import text

class ProductReview:
    def __init__(self, prod_review_id, product_key, seller_key, person_reviewing_id, review_rating, review_description, review_image, product_name):
        self.prod_review_id = prod_review_id
        self.product_key = product_key
        self.seller_key = seller_key
        self.person_reviewing_id = person_reviewing_id
        self.review_rating = review_rating
        self.review_description = review_description
        self.review_image = review_image
        self.product_name = product_name

    @staticmethod
    def get(prod_review_id):
        rows = app.db.execute('''
SELECT prod_review_id, product_key, seller_key, person_reviewing_id, review_rating, review_description, review_image, Products.product_name
FROM ProductReviews 
WHERE prod_review_id = :prod_review_id JOIN products ON
ProductReviews.product_key = Products.product_key AND
ProductReviews.seller_key = Products.seller_key
ORDER BY prod_review_id DESC
''',
                              prod_review_id=prod_review_id)
        return ProductReview(*(rows[0])) if rows else None

    @staticmethod
    def get_all_for_product(product_key): # get all reviews for a product
        rows = app.db.execute('''
SELECT prod_review_id, product_key, seller_key, person_reviewing_id, review_rating, review_description, review_image
FROM ProductReviews
WHERE product_key = :product_key
ORDER BY prod_review_id DESC
''',
                              product_key=product_key)
        return [ProductReview(*row) for row in rows]

    @staticmethod
    def get_all_by_user(person_reviewing_id, sort_order='rating_desc'):
        # Define a mapping from sort_order keys to SQL
        sort_options = {
            'rating_desc': 'review_rating DESC',
            'rating_asc': 'review_rating ASC',
            'date_desc': 'prod_review_id DESC',  # Assuming the ID is sequential and indicative of date
            'date_asc': 'prod_review_id ASC',
            'name_asc': 'Products.product_name ASC',
            'name_desc': 'Products.product_name DESC'
        }

        # Get the correct ORDER BY clause from the sort_options dict
        order_by = sort_options.get(sort_order, 'review_rating DESC')

        # Execute the SQL query with dynamic ORDER BY clause
        sql_query = f'''
        SELECT prod_review_id, ProductReviews.product_key, ProductReviews.seller_key, person_reviewing_id, review_rating, review_description, review_image, Products.product_name
        FROM ProductReviews
        JOIN Products ON ProductReviews.product_key = Products.product_key AND ProductReviews.seller_key = Products.seller_key
        WHERE person_reviewing_id = :person_reviewing_id
        ORDER BY {order_by}
        '''
        rows = app.db.execute(sql_query, person_reviewing_id=person_reviewing_id)
        return [ProductReview(*row) for row in rows]

    
    @staticmethod
    def get_recent_by_user(person_reviewing_id): # get the 5 most recent reviews by a user
        rows = app.db.execute('''
SELECT prod_review_id, ProductReviews.product_key, ProductReviews.seller_key, person_reviewing_id, review_rating, review_description, review_image, Products.product_name
FROM ProductReviews, Products
WHERE person_reviewing_id = :person_reviewing_id AND
ProductReviews.product_key = Products.product_key AND
ProductReviews.seller_key = Products.seller_key
ORDER BY prod_review_id DESC
LIMIT 5
''',
                              person_reviewing_id=person_reviewing_id)
        return [ProductReview(*row) for row in rows]
    
    @staticmethod
    def get_seller_reviews(seller_key, page=1, per_page=10): # get all reviews for a seller
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT prod_review_id, ProductReviews.product_key, ProductReviews.seller_key, person_reviewing_id, review_rating, review_description, review_image, Products.product_name
FROM ProductReviews, Products
WHERE ProductReviews.seller_key = :seller_key AND
ProductReviews.product_key = Products.product_key AND
ProductReviews.seller_key = Products.seller_key
ORDER BY prod_review_id DESC
LIMIT :limit OFFSET :offset
''',
                              seller_key=seller_key, limit=per_page, offset=offset)
        return [ProductReview(*row) for row in rows] if rows else []
    
    @staticmethod
    def get_seller_review_count(seller_key):
        count = app.db.execute('''
SELECT COUNT(*)
FROM ProductReviews
WHERE seller_key = :seller_key
''',
                              seller_key=seller_key)
        return int(count[0][0])
    
    #Add Review
    @staticmethod
    def add_review(order_id, rating, description):
        # Fetch product_key and user_id from OrderHistory based on order_id
        order = app.db.execute("""
        SELECT product_key, seller_key, buyer_key FROM OrderHistory WHERE order_id = :order_id
        """, {'order_id': order_id}).fetchone()
        
        if not order:
            print("Order not found")
            return False

        product_key, seller_key, user_id = order

        # Insert review
        rows = app.db.execute("""
        INSERT INTO ProductReviews (product_key, seller_key, person_reviewing_id, review_rating, review_description)
        VALUES (:product_key, :seller_key, :user_id, :rating, :description)
        RETURNING prod_review_id
        """,
            product_key=product_key,
            seller_key=seller_key,
            user_id=user_id,
            rating=rating,
            description=description
        )
        prod_review_id = rows[0][0]
        return ProductReview.get(prod_review_id)