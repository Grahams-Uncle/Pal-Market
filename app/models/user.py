from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
import decimal
import re

from .. import login

class Address(UserMixin):
    def __init__(self, address_key):
        address = self.address_string(address_key)
        self.street_num = address[0]
        self.street_name = address[1]
        self.city_name = address[2]
        self.state = address[3]
        self.zipcode = address[4]
        
    def address_string(self, address_key):
        rows = app.db.execute("""
        SELECT Address_Table.street_num, Address_Table.street_name, Zipcode.city, Zipcode.state_id, Zipcode.zipcode
        FROM Address_Table JOIN Zipcode ON Address_Table.zipcode = Zipcode.zipcode
        WHERE address_key = :address_key
        """,
            address_key = address_key)
        
        return rows[0]
         
        #return f'{rows[0][0]} {rows[0][1]} {rows[0][2]}, {rows[0][3]} {rows[0][4]}'


class User(UserMixin):
    def __init__(self, id, email, password, user_ship_address, user_bill_address, user_balance, user_rating, user_bio, is_seller, firstname, lastname):
        self.id = id
        self.email = email
        self.password = password
        self.ship_key = user_ship_address
        self.bill_key = user_bill_address
        self.ship_address = Address(user_ship_address)
        self.bill_address = Address(user_bill_address)
        self.balance = user_balance
        self.rating = round(user_rating, 2)
        self.bio = user_bio
        self.is_seller = is_seller
        self.firstname = firstname
        self.lastname = lastname


    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT id, email, password, user_ship_address, user_bill_address, user_balance, COALESCE(AVG(review_rating), 5.0), user_bio, is_seller, firstname, lastname
FROM Users
LEFT JOIN UserReviews ON id = person_key
WHERE email = :email
GROUP BY id, email, password, user_ship_address, user_bill_address, user_balance, user_bio, is_seller, firstname, lastname
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][2], password):
             return None
        # elif rows[0][2] != password:
        #     return None
        else:
            return User(*rows[0])

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
    SELECT email
    FROM Users
    WHERE email = :email
    """,
                              email=email)
        return True if len(rows) > 0 else False
    
    @staticmethod
    def email_valid(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b' #regular expression for email
        
        if(re.fullmatch(regex, email)):
            return True
        else:
            return False
    
    @staticmethod
    def get_address_key(number, street, zipcode):
        rows = app.db.execute("""
    SELECT address_key
    FROM Address_Table
    WHERE street_num = :street_num AND street_name = :street_name AND zipcode = :zipcode
    """,
        street_num = number,
        street_name = street,
        zipcode = zipcode)
        if rows:
            return rows[0][0]
        else:
            return None
    
    @staticmethod
    def create_address_key(address_number, address_street, address_zip):
        rows = app.db.execute("""
        INSERT INTO Address_Table(street_num, street_name, zipcode)
        VALUES(:address_number, :address_street, :address_zip)
        RETURNING address_key
        """,
            address_number=address_number,
            address_street=address_street,
            address_zip=address_zip)

        address_key = rows[0][0]
        return address_key
    
    @staticmethod
    def get_address(address_key):
        rows = app.db.execute("""
        SELECT Address_Table.street_num, Address_Table.street_name, Zipcode.zipcode, Zipcode.city, Zipcode.state
        FROM Address_Table, Zipcode
        WHERE address_key = :address_key
              AND Address_Table.zipcode = Zipcode.zipcode
        """,
            address_key = address_key)
            
        return rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4] if len(rows) > 0 else None

    @staticmethod
    def register(email, password, address_number, address_street, address_zip, starting_balance, firstname, lastname):
        if not User.email_valid(email):
            return None

        if User.email_exists(email):
            return None

        address_key = User.get_address_key(address_number, address_street, address_zip)
        
        if address_key is None:
            address_key = User.create_address_key(address_number, address_street, address_zip)

        rows = app.db.execute("""
        INSERT INTO Users(email, password, user_ship_address, user_bill_address, user_balance, firstname, lastname)
        VALUES(:email, :password, :shipping_address, :billing_address, :starting_balance, :firstname, :lastname)
        RETURNING id
        """,
            email=email,
            password=generate_password_hash(password),
            shipping_address=address_key,
            billing_address=address_key,
            starting_balance=starting_balance,
            firstname=firstname, 
            lastname=lastname)
        
        id = rows[0][0]
        return User.get(id)
    
    @staticmethod
    def edit_balance(id, add, balance):
        old_user = User.get(id)
        if old_user is None: return None

        try:
            balance = float(balance)
            balance = decimal.Decimal(balance)
            if balance < 0: return None
        except:
            return None

        new_balance = old_user.balance + balance if add else old_user.balance - balance

        if new_balance >= 0.0:
            rows = app.db.execute(
            """
            UPDATE Users
            SET user_balance = :user_balance
            WHERE id = :id
            """,
                id=id,
                user_balance=new_balance)
        else:
            return None

        return id if rows != 0 else None

    @staticmethod
    def edit_info(id, ship_address_number, ship_address_street, ship_address_zip, bill_address_number, bill_address_street, bill_address_zip, user_bio, firstname, lastname, old_password, new_password, new_password2, email):
        old_user = User.get(id)
        if old_user is None: return None

        # Find address_key for shipping address
        if len(ship_address_number) > 0 or len(ship_address_street) > 0 or len(ship_address_zip) > 0:
            if len(ship_address_zip) > 0:
                tmp = app.db.execute(
                    """
                    SELECT *
                    FROM Zipcode
                    WHERE zipcode = :zipcode
                    """,
                        zipcode=ship_address_zip)

                if len(tmp) == 0:
                    return None

            old_ship_address_number, old_ship_address_street, old_ship_address_zip, _, _ = User.get_address(old_user.ship_key)
            
            ship_address_number = ship_address_number if len(ship_address_number) > 0 else old_ship_address_number
            ship_address_street = ship_address_street if len(ship_address_street) > 0 else old_ship_address_street
            ship_address_zip = ship_address_zip if len(ship_address_zip) > 0 else old_ship_address_zip
            
            user_ship_address = User.get_address_key(ship_address_number, ship_address_street, ship_address_zip)
            if user_ship_address is None:
                user_ship_address = User.create_address_key(ship_address_number, ship_address_street, ship_address_zip)
        else:
            user_ship_address = old_user.ship_key

        # Find address_key for billing address
        if len(bill_address_number) > 0 or len(bill_address_street) > 0 or len(bill_address_zip) > 0:
            if len(bill_address_zip) > 0:
                tmp = app.db.execute(
                    """
                    SELECT *
                    FROM Zipcode
                    WHERE zipcode = :zipcode
                    """,
                        zipcode=bill_address_zip)

                if len(tmp) == 0:
                    return None
            old_bill_address_number, old_bill_address_street, old_bill_address_zip, _, _ = User.get_address(old_user.bill_key)
            
            bill_address_number = bill_address_number if len(bill_address_number) > 0 else old_bill_address_number
            bill_address_street = bill_address_street if len(bill_address_street) > 0 else old_bill_address_street
            bill_address_zip = bill_address_zip if len(bill_address_zip) > 0 else old_bill_address_zip
            
            user_bill_address = User.get_address_key(bill_address_number, bill_address_street, bill_address_zip)
            if user_bill_address is None:
                user_bill_address = User.create_address_key(bill_address_number, bill_address_street, bill_address_zip)
        else:
            user_bill_address = old_user.bill_key

        if len(old_password) > 0 or len(new_password) > 0 or len(new_password2):
            if not (len(old_password) > 0 and len(new_password) > 0 and len(new_password2)):
                return None
            if (not check_password_hash(old_user.password, old_password)) or (new_password != new_password2):
                return None
            
            password = generate_password_hash(new_password)
        else:
            password = old_user.password

        if len(email) > 0:
            if not User.email_valid(email):
                return None

            if User.email_exists(email):
                return None
        else:
            email = old_user.email

        rows = app.db.execute(
        """
        UPDATE Users
        SET password = :password, user_ship_address = :user_ship_address, user_bill_address = :user_bill_address, user_bio = :user_bio, firstname = :firstname, lastname = :lastname, email = :email
        WHERE id = :id
        """,
            id=id,
            password=password,
            user_ship_address=user_ship_address,
            user_bill_address=user_bill_address,
            user_bio=user_bio if len(user_bio) > 0 else old_user.bio,
            firstname=firstname if len(firstname) > 0 else old_user.firstname,
            lastname=lastname if len(lastname) > 0 else old_user.lastname,
            email=email)

        return id if rows != 0 else None


    @staticmethod
    def convert_to_seller(id):
        rows = app.db.execute(
        """
        UPDATE Users
        SET is_seller = true
        WHERE id = :id
        """,
            id=id)

        return True if rows != 0 else False

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, password, user_ship_address, user_bill_address, user_balance, COALESCE(AVG(review_rating), 5.0) AS avg_rating, user_bio, is_seller, firstname, lastname
FROM Users
LEFT JOIN UserReviews ON id = person_key
WHERE id = :id
GROUP BY id, email, password, user_ship_address, user_bill_address, user_balance, user_bio, is_seller, firstname, lastname
""",
                              id=id)
        return User(*rows[0]) if rows else None
    

    
