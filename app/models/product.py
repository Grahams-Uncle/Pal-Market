from flask import current_app as app


class Product:
    # def __init__(self,product_key, seller_key, cat_key, product_name, product_description, product_price, product_image, available, product_rating = None, product_discount_code = None):
    #     self.product_key = product_key
    #     self.seller_key = seller_key
    #     self.cat_key = cat_key
    #     self.product_name = product_name
    #     self.product_description = product_description
    #     self.product_price = product_price
    #     self.product_image = product_image
    #     self.product_discount_code = product_discount_code
    #     self.available = available
    #     self.product_rating = product_rating
    def __init__(self, product_key, seller_key, cat_key, product_name, product_description, product_price, product_image, available, product_rating = None, product_discount_code = None,sellerFirst = None, sellerSecond = None):
        self.product_key = product_key
        self.seller_key = seller_key
        self.cat_key = cat_key
        self.product_name = product_name
        self.product_description = product_description
        self.product_price = product_price
        self.product_image = product_image
        self.product_discount_code = product_discount_code
        self.available = available
        self.product_rating = product_rating
        self.sellerFirst = sellerFirst
        self.sellerSecond = sellerSecond

    @staticmethod
    def getSize(search_term=None, seller_search = None, category_id = None, max_price=None, sort_by=None, order=None, topk = None):
        cond = []
        params = {}
        cond.append("available = True")
        if search_term:
            cond.append("Products.product_name ILIKE :search")
            params['search'] = f'%{search_term}%'
        if seller_search:
            cond.append("CONCAT_WS(' ', Users.firstname, Users.lastname) ILIKE :seller_search")
            params['seller_search'] = f'%{seller_search}%'
        if max_price is not None:
            cond.append("Products.product_price <= :maxP")
            params['maxP'] = max_price
        
        if category_id:
            cond.append("Products.cat_key = :category_id")
            params['category_id'] = category_id
        where_clause = " AND ".join(cond) if cond else "0=0"
        
        query = f'''
    SELECT product_key, seller_key, cat_key, product_name, product_description, product_price, product_image, available,product_rating, Products.product_discount_code, Users.firstname, Users.lastname
    FROM Products
    JOIN Users on (Users.id = seller_key) and Users.is_seller = True
    WHERE {where_clause}
    '''
        rows = app.db.execute(query, **params)
        return [Product(*row) for row in rows]

    @staticmethod
    def filter_products(search_term=None, seller_search = None, category_id = None, max_price=None, sort_by=None, order=None, topk = None, page = None, per_page = None):
        cond = []
        params = {}
        cond.append("available = True")
        if search_term:
            cond.append("Products.product_name ILIKE :search")
            params['search'] = f'%{search_term}%'
        if seller_search:
            cond.append("CONCAT_WS(' ', Users.firstname, Users.lastname) ILIKE :seller_search")
            params['seller_search'] = f'%{seller_search}%'
        if max_price is not None:
            cond.append("Products.product_price <= :maxP")
            params['maxP'] = max_price
        
        if category_id:
            cond.append("Products.cat_key = :category_id")
            params['category_id'] = category_id
        where_clause = " AND ".join(cond) if cond else "0=0"
        
    #     query = f'''
    # SELECT Products.product_key, Products.seller_key, Products.cat_key, Products.product_name, Products.product_description, Products.product_price, Products.product_image, Products.available, COALESCE(avg_reviews.avg_rating, 0) AS average_rating
    # FROM Products
    # LEFT JOIN (
    #     SELECT ProductReviews.product_key, ROUND(AVG(ProductReviews.review_rating), 2) AS avg_rating
    #     FROM ProductReviews
    #     GROUP BY ProductReviews.product_key
    # ) AS avg_reviews ON Products.product_key = avg_reviews.product_key
    # WHERE {where_clause} 
    # '''
        query = f'''
        SELECT Products.product_key, Products.seller_key, Products.cat_key, Products.product_name, Products.product_description, Products.product_price, Products.product_image, Products.available, COALESCE(avg_reviews.avg_rating, 0) AS average_rating, Products.product_discount_code, Users.firstname, Users.lastname
        FROM Products
        LEFT JOIN (
            SELECT ProductReviews.product_key, ROUND(AVG(ProductReviews.review_rating), 2) AS avg_rating
            FROM ProductReviews
            GROUP BY ProductReviews.product_key
        ) AS avg_reviews ON Products.product_key = avg_reviews.product_key
        JOIN Users on Users.id = Products.seller_key and Users.is_seller = True
        WHERE {where_clause} 
        '''
        mydict = {"Ascending": "ASC", "Descending":"DESC"}
        if order in mydict:
            query += f' ORDER BY Products.{sort_by} {mydict[order]}'
        if topk:
            query+=f" LIMIT {topk}"
        else:
            offset = (page - 1) * per_page
            query+= f' LIMIT {per_page} OFFSET {offset}'
        rows = app.db.execute(query, **params)
        return [Product(*row) for row in rows]
    @staticmethod
    def get(curk):
        rows = app.db.execute('''
        SELECT product_key, seller_key, cat_key, product_name, product_description, product_price, product_image, available
        FROM Products
        WHERE product_key = :curk
        ''',
                                    curk=curk)
        return [Product(*row) for row in rows] if rows is not None else None
        #return Product(*(rows[0])) if rows is not None else None
    
    @staticmethod
    def get_seller(seller_key,curk):
        rows = app.db.execute('''
        SELECT product_key, seller_key, cat_key, product_name, product_description, product_price, product_image, available
        FROM Products
        WHERE product_key = :curk AND seller_key = :seller_key
        ''', curk=curk, seller_key=seller_key)
        return [Product(*row) for row in rows] if rows is not None else None
    
    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
                SELECT product_key, seller_key, cat_key, product_name, product_description, product_price, product_image, available
                FROM Products
                WHERE available = :available
                ''',
                                            available=available)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_top_k(k):
        rows = app.db.execute('''
SELECT product_key, seller_key, cat_key, product_name, product_description, product_price, product_image, available
FROM Products
ORDER BY product_price DESC LIMIT :k
''',
                              k=k)
        return [Product(*row) for row in rows]
