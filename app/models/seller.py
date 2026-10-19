from flask import current_app as app


class Seller:
    def __init__(self, id, lastname, firstname, city, state, user_rating, items_sold):
        self.id = id
        self.name =  firstname + " " + lastname
        self.user_rating = user_rating
        self.item_sold = items_sold
        self.state = state
        self.city = city

    @staticmethod
    def is_seller(seller_id):
        row = app.db.execute('''
                SELECT Users.is_seller
                FROM Users
                WHERE Users.id = :id
            ''', id=seller_id)
        return bool(row[0][0]) if row !=[] else None

    @staticmethod
    def get_count(rating=0, selected_state="All"):

        # Validate states
        valid_states = ['Kansas', 'Oregon', 'Texas', 'Idaho', 'Alaska', 'Alabama', 'Oklahoma', 'Colorado', 'North Carolina', 'Mississippi', 'Florida', 'Delaware', 'Vermont', 'Virgin Islands', 'Northern Mariana Islands', 'Nevada', 'Louisiana', 'Guam', 'New York', 'West Virginia', 'South Carolina', 'New Jersey', 'Hawaii', 'New Mexico', 'Arkansas', 'Missouri', 'Connecticut', 'South Dakota', 'District of Columbia', 'Iowa', 'Indiana', 'Massachusetts', 'Rhode Island', 'Ohio', 'American Samoa', 'Michigan', 'Minnesota', 'Pennsylvania', 'Washington', 'Montana', 'Wisconsin', 'Kentucky', 'Arizona', 'Illinois', 'Virginia', 'Maryland', 'Georgia', 'Puerto Rico', 'Utah', 'Wyoming', 'New Hampshire', 'North Dakota', 'California', 'Nebraska', 'Maine', 'Tennessee']
        if selected_state in valid_states:
            state = f"AND User_Info.state = '{selected_state}'"
        else:
            state = None

        sql_query = '''
            WITH User_Info AS (
                SELECT Users.id,
                    Users.lastname,
                    Users.firstname,
                    Zipcode.city,
                    Zipcode.state,
                    SUM(OrderHistory.order_quantity) AS items_sold
                FROM Users
                JOIN Address_Table ON Users.user_ship_address = Address_Table.address_key
                JOIN Zipcode ON Address_Table.zipcode = Zipcode.zipcode
                LEFT OUTER JOIN OrderHistory ON Users.id = OrderHistory.seller_key
                WHERE Users.is_seller = True 
                GROUP BY Users.id, Users.lastname, Users.firstname,Zipcode.city,Zipcode.state
            ),
            User_rating AS (
                SELECT Users.id, COALESCE(AVG(UserReviews.review_rating), 5) AS user_rating
                FROM Users LEFT OUTER JOIN UserReviews ON UserReviews.person_key = Users.id
                GROUP BY Users.id
            )
            SELECT COUNT(DISTINCT User_Info.id)
            FROM User_Info JOIN User_rating ON User_Info.id = User_rating.id
                 AND User_rating.user_rating >= :rating
        '''

        # Conditionally add state filter if state is not None
        if state is not None:
            sql_query += state

        count = app.db.execute(sql_query, rating=rating)
        return int(count[0][0])

    @staticmethod
    def all_states():
        states = app.db.execute('''
            SELECT DISTINCT state
            FROM Zipcode JOIN Address_Table ON Zipcode.zipcode = Address_Table.zipcode
                JOIN Users ON Users.user_ship_address = Address_Table.address_key
                WHERE Users.is_seller
        ''')
        return states

    @staticmethod
    def get_all(sort_criteria="name", order="ASC", rating=0, selected_state="All", page=1, per_page=15):
        offset = (page - 1) * per_page
        # Validate order
        if order.upper() not in ["ASC", "DESC"]:
            order = "ASC"
        sorting_criteria_map = {
            "name": f"User_Info.firstname {order}, User_Info.lastname",  
            "rating": "User_rating.user_rating",
            "sold": "User_Info.items_sold" 
        }

        # Validate sort_criteria
        if sort_criteria not in sorting_criteria_map:
            sort_criteria = f"User_Info.firstname {order}, User_Info.lastname"

        # Validate states
        valid_states = ['Kansas', 'Oregon', 'Texas', 'Idaho', 'Alaska', 'Alabama', 'Oklahoma', 'Colorado', 'North Carolina', 'Mississippi', 'Florida', 'Delaware', 'Vermont', 'Virgin Islands', 'Northern Mariana Islands', 'Nevada', 'Louisiana', 'Guam', 'New York', 'West Virginia', 'South Carolina', 'New Jersey', 'Hawaii', 'New Mexico', 'Arkansas', 'Missouri', 'Connecticut', 'South Dakota', 'District of Columbia', 'Iowa', 'Indiana', 'Massachusetts', 'Rhode Island', 'Ohio', 'American Samoa', 'Michigan', 'Minnesota', 'Pennsylvania', 'Washington', 'Montana', 'Wisconsin', 'Kentucky', 'Arizona', 'Illinois', 'Virginia', 'Maryland', 'Georgia', 'Puerto Rico', 'Utah', 'Wyoming', 'New Hampshire', 'North Dakota', 'California', 'Nebraska', 'Maine', 'Tennessee']
        if selected_state in valid_states:
            state = f"AND User_Info.state = '{selected_state}'"
        else:
            state = None

        sql_query = '''
            WITH User_Info AS (
                SELECT Users.id,
                    Users.lastname,
                    Users.firstname,
                    Zipcode.city,
                    Zipcode.state,
                    SUM(OrderHistory.order_quantity) AS items_sold
                FROM Users
                JOIN Address_Table ON Users.user_ship_address = Address_Table.address_key
                JOIN Zipcode ON Address_Table.zipcode = Zipcode.zipcode
                LEFT OUTER JOIN OrderHistory ON Users.id = OrderHistory.seller_key
                WHERE Users.is_seller = True 
                GROUP BY Users.id, Users.lastname, Users.firstname,Zipcode.city,Zipcode.state
            ),
            User_rating AS (
                SELECT Users.id, COALESCE(AVG(UserReviews.review_rating), 5) AS user_rating
                FROM Users LEFT OUTER JOIN UserReviews ON UserReviews.person_key = Users.id
                GROUP BY Users.id
            )
            SELECT User_Info.id, User_Info.lastname, User_Info.firstname, User_Info.city, User_Info.state, User_rating.user_rating, User_Info.items_sold
            FROM User_Info JOIN User_rating ON User_Info.id = User_rating.id
                 AND User_rating.user_rating >= :rating
        '''
        # Conditionally add state filter if state is not None
        if state is not None:
            sql_query += state

        sql_query += f'''
            ORDER BY {sorting_criteria_map.get(sort_criteria)} {order}
            LIMIT :limit OFFSET :offset;
        '''

        rows = app.db.execute(sql_query, limit=per_page, offset=offset, rating=rating)
        return [Seller(*row) for row in rows]
    
    @staticmethod
    def order_fulfill(sale_id, product_key, seller_id):
        row = app.db.execute('''
            UPDATE OrderHistory
            SET is_fulfilled = 't', fulfillment_time = NOW()
            WHERE order_id = :sale_id AND product_key = :product_key AND seller_key = :seller_id
        ''', sale_id=sale_id, product_key=product_key, seller_id=seller_id)
        return row
