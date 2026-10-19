from flask import current_app as app
import random
from sqlalchemy import text

class Inventory:
    def __init__(self, product_key, seller_key, product_name, cat_key, product_description, product_price, product_rating, quantity, product_image, discount_key, discount_amount ):
        self.product_key = product_key
        self.seller_key = seller_key
        self.product_name = product_name
        self.cat_key = cat_key
        self.product_description =product_description
        self.product_price = product_price
        self.product_rating = product_rating
        self.quantity = quantity
        self.image = product_image
        self.discount_code = discount_key
        self.discount_amount = discount_amount

    @staticmethod
    def get_seller_products(seller_key, sort='pname', order='asc',  product_name=None, page=1, per_page=20, is_seller=False):
        offset = (page - 1) * per_page
        sql_query = '''
                    SELECT Inventory.product_key, Inventory.seller_key, product_name, cat_key, product_description, product_price, COALESCE(AVG(ProductReviews.review_rating), 5), quantity, product_image, Discounts.discount_key, Discounts.discount_amount
                    FROM Inventory JOIN Products ON Products.seller_key = Inventory.seller_key AND Products.product_key = Inventory.product_key
                        LEFT OUTER JOIN ProductReviews ON Inventory.seller_key = ProductReviews.seller_key AND Inventory.product_key = ProductReviews.product_key
                        LEFT OUTER JOIN Discounts ON Products.product_discount_code = Discounts.discount_key
                    WHERE Inventory.seller_key = :seller_key 
                        AND Products.seller_key = Inventory.seller_key
                        AND Products.available = True 
                    '''
        params = {"seller_key":seller_key, "limit":per_page, "offset":offset}
        if product_name:
            sql_query += 'AND product_name = :product_name '
            params["product_name"] = product_name

        if not is_seller: # Hide 0 quantity products from buyers
            sql_query += 'AND Inventory.quantity > 0 '

        sql_query += ''' GROUP BY Inventory.product_key, Inventory.seller_key, product_name, cat_key, product_description, product_price, quantity, product_image, Discounts.discount_key, Discounts.discount_amount '''
        query_map = {
                "pname":'ORDER BY product_name ',
                "qty":'ORDER BY quantity ',
                "price":'ORDER BY product_price '
            }

        sql_query += query_map[sort] + order.upper()
        
        sql_query += ''' LIMIT :limit OFFSET :offset; '''

        with app.db.engine.begin() as conn:
            rows = conn.execute(text(sql_query), params).fetchall()
        return [Inventory(*row) for row in rows] if rows else []

    @staticmethod
    def get_seller_product(seller_key, product_key):
        row = app.db.execute('''
            SELECT Inventory.product_key, Inventory.seller_key, product_name, cat_key, product_description, product_price, COALESCE(AVG(ProductReviews.review_rating), 5), quantity, product_image, Discounts.discount_key, Discounts.discount_amount
            FROM Inventory JOIN Products ON Products.seller_key = Inventory.seller_key AND Products.product_key = Inventory.product_key
                 LEFT OUTER JOIN ProductReviews ON Inventory.seller_key = ProductReviews.seller_key AND Inventory.product_key = ProductReviews.product_key
                 LEFT OUTER JOIN Discounts ON Products.product_discount_code = Discounts.discount_key
            WHERE Inventory.seller_key = :seller_key 
                AND Inventory.product_key = :product_key 
                AND Products.available = True
            GROUP BY Inventory.product_key, Inventory.seller_key, product_name, cat_key, product_description, product_price, quantity, product_image, Discounts.discount_key, Discounts.discount_amount
            ''', seller_key=seller_key, product_key=product_key)
        return Inventory(*row[0]) if row else None 

    
    @staticmethod
    def get_product_inventory(seller_key, product_key):
        count = app.db.execute('''
            SELECT Inventory.quantity
            FROM Inventory,Products
            WHERE Inventory.seller_key = :seller_id
                  AND Inventory.product_key = :product_key
                  AND Products.available = True;
        ''', seller_id=seller_key, product_key=product_key)
        return int(count[0][0])
    
    @staticmethod
    def get_inventory_count(seller_key, is_seller=False):
        # Count the total number of products in inventory
        if is_seller:
            count = app.db.execute('''
                SELECT COUNT(Inventory.product_key)
                FROM Inventory, Products
                WHERE Inventory.seller_key = :seller_id 
                    AND Products.seller_key = Inventory.seller_key 
                    AND Inventory.product_key = Products.product_key
                    AND Products.available = True;
            ''', seller_id=seller_key)
        else:
            count = app.db.execute('''
                SELECT COUNT(Inventory.product_key)
                FROM Inventory, Products
                WHERE Inventory.seller_key = :seller_id AND
                    Products.seller_key = Inventory.seller_key AND
                    Inventory.product_key = Products.product_key AND
                    Inventory.quantity>0
                    AND Products.available = True;
            ''', seller_id=seller_key)
        return int(count[0][0])
    
    @staticmethod
    def update_inventory(seller_key, product_key, change):
        new_qty = Inventory.get_product_inventory(seller_key, product_key) + change
        app.db.execute('''
                        UPDATE Inventory
                        SET quantity = :new_qty
                        WHERE product_key = :product_key AND seller_key = :seller_id
                        ''', product_key=product_key, seller_id=seller_key, new_qty=new_qty)
        
    @staticmethod
    def update_product_info(seller_key, product_key, cat_key, product_description, product_quantity, discount_code):
        try:
            product_name = app.db.execute('''
                        SELECT product_name 
                        FROM Products
                        WHERE seller_key = :seller_key
                        AND product_key = :product_key
                        AND Products.available = True;
                    ''', seller_key=seller_key, product_key=product_key)[0][0]
            with app.db.engine.begin() as conn:
                conn.execute(text("""
                    UPDATE Products
                    SET product_description = :new_description,
                        available = True,
                        product_discount_code = :product_discount_code,
                        cat_key = :cat_key
                    WHERE product_key = :product_key AND seller_key = :seller_key
                """), {
                    "product_key": product_key,
                    "seller_key": seller_key,
                    "new_description": product_description,
                    "product_discount_code": discount_code,
                    "cat_key":cat_key
                })

                conn.execute(
                    text('''
                            UPDATE Inventory
                            SET quantity = :new_qty
                            WHERE product_key = :product_key AND seller_key = :seller_id
                        '''),
                    {
                        "product_key": product_key,
                        "seller_id":seller_key,
                        "new_qty":product_quantity,
                    }
                )
                conn.commit()
                return f"Product {product_name} updated successfully!"
        except Exception as e:
            conn.rollback()
            return f"Error! Product {product_name} failed to update! {e}"
        finally:
            # Close the database connection
            conn.close()

    @staticmethod
    def addCode(discount_amount):
        with app.db.engine.begin() as conn:
            newCode = conn.execute(text('''INSERT INTO Discounts (discount_amount)
            VALUES (:product_discount_amount) RETURNING discount_key'''),
            {"product_discount_amount": discount_amount})
            discount_code = newCode.fetchone()[0]
            conn.commit()
        return discount_code
    
    @staticmethod
    def updateCode(discount_code, discount_amount):
        with app.db.engine.begin() as conn:
            code = conn.execute(text("""
                            UPDATE Discounts
                            SET discount_amount = :new_discount_amount
                            WHERE discount_key = :discount_key
                            RETURNING discount_key
                        """),
                {
                    "discount_key": discount_code,
                    "new_discount_amount": discount_amount
                })
            discount_code = code.fetchone()[0]
            conn.commit()
        return discount_code
    
    @staticmethod
    def deleteCode(discount_code):
        with app.db.engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM Discounts
                WHERE discount_key = :discount_key
            """),
            {"discount_key": discount_code})
            conn.commit()
        return discount_code

    @staticmethod
    def add_product(seller_key, prod_name, product_category, product_description, product_price, product_quantity, discount_code):
        try:
            with app.db.engine.begin() as conn:
                # Add new product to Products table
                active_products = conn.execute(text("""
                                        SELECT product_name, available
                                        FROM Products
                                        WHERE seller_key = :seller_key
                                        AND available = True
                                    """), {"seller_key": seller_key})

                product_names = [name[0] for name in active_products]

                if prod_name in product_names:
                    return f"You already have {prod_name} posted! Update your inventory instead!"

                product_key = conn.execute(text("""
                                    INSERT INTO Products (seller_key, cat_key, product_name, product_description, product_price, product_image, product_discount_code, available)
                                    VALUES(:seller_key, :cat_key, :product_name, :product_description, :product_price, :product_image, :product_discount_code, :available)
                                    RETURNING product_key
                                """), {
                                    "seller_key": seller_key,
                                    "cat_key": product_category,
                                    "product_name": prod_name,
                                    "product_description": product_description,
                                    "product_price": product_price,
                                    "product_image": f"/image/{prod_name}.png",
                                    "product_discount_code": discount_code,
                                    "available": True,
                                }).fetchone()[0]

                # Add new product to Inventory table
                conn.execute(text("""
                    INSERT INTO Inventory (product_key, seller_key, quantity)
                    VALUES(:product_key, :seller_key, :quantity)
                """), {
                    "seller_key": seller_key,
                    "quantity": product_quantity,
                    "product_key": product_key
                })

                # Commit the transaction
                conn.commit()
                if discount_code:
                    return f"Product {prod_name} posted successfully!"
                else:
                    return f"Product {prod_name} posted successfully! Your discount code is {discount_code}"
        except Exception as e:
            # Rollback the transaction if an error occurs
            conn.rollback()
            return f"Error! Product {prod_name} not posted!\n {e}"

        finally:
            # Close the database connection
            conn.close()

    @staticmethod
    def delete_product(seller_key, product_key):
        try:
            product_name = app.db.execute('''
                                    SELECT product_name
                                    FROM Products
                                    WHERE seller_key = :seller_key
                                    AND product_key = :product_key
                                    AND Products.available = True;
                                ''', seller_key=seller_key, product_key=product_key)[0]
            with app.db.engine.begin() as conn:
                conn.execute(text("""
                    UPDATE Products
                    SET available = False, product_discount_code=NULL
                    WHERE product_key = :product_key
                    AND seller_key = :seller_key;
                    """), {"seller_key": seller_key, 
                           "product_key":product_key}
                    )
                conn.execute(text("""
                    DELETE FROM Inventory
                    WHERE product_key = :product_key
                    AND seller_key = :seller_key;
                    """), {"seller_key": seller_key, 
                           "product_key":product_key}
                    )
                conn.commit()
                return f"Product {product_name[0]} deleted successfully!"
        except Exception as e:
            # Rollback the transaction if an error occurs
            conn.rollback()
            return f"Error! Product {product_name[0]} not deleted!\n {e}"
        finally:
            # Close the database connection
            conn.close()
