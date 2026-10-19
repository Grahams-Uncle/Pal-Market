from flask import render_template, flash, redirect, url_for, request
from flask import current_app as app
from flask_login import current_user, login_required
from .models.seller import Seller
from .models.product import Product
from .models.inventory import Inventory
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from flask import Blueprint
import math
from sqlalchemy import text
bp = Blueprint('products', __name__)

class SearchForm(FlaskForm):
    product_id = IntegerField('Filter by top k items', validators=[DataRequired()])
    submit = SubmitField('Search')

@bp.route('/Products', methods=['POST', 'GET'])
def search_product():
    #print (current_user.id, "USER IS HERERERE", current_user.firstname)
    search_term = request.args.get('search_term', None)
    seller_search = request.args.get('seller_search', None)
    max_price = request.args.get('max_price', None, type=float)
    category_id = request.args.get('product_category', None, type=int)
    sort_by = request.args.get('sort_by', None, type = str)
    order = request.args.get('order', None, type = str)
    topk = request.args.get('topk1', None, type = int)
    # min_avg_rating = request.args.get('min_avg_rating', None, type=int)
    # codes = app.db.execute('''SELECT discount_key from Discounts''')
    # codeSet = set()
    # for x in codes:
    #     codeSet.add(x[0])
    # print (codeSet, "CODE SET HERE")
    max_price = None if max_price == 0 else max_price
    curpage = request.args.get('curpage', type=int, default=1)
    npage = 10
    form = SearchForm()
    categories = app.db.execute('''SELECT cat_key, cat_name FROM Product_Category ORDER BY cat_name''')
    product = Product.filter_products(search_term, seller_search, category_id, max_price, sort_by, order, topk, curpage, npage)
    n = len(Product.getSize(search_term, seller_search, category_id, max_price, sort_by, order, topk))
    totalpage = math.ceil(n/npage)
    flag = False
    try:
        flag = current_user.is_seller
    except:
        flag = False
    print ("flag", flag)
    return render_template('product.html', products=product, form = form, categories = categories, curpage = curpage, totalpage = totalpage, curuser = current_user, flag = flag)
@bp.route('/Products/<int:product_key>', methods=['GET', 'POST'])
@login_required
def curproduct(product_key):
    prods = Product.get(product_key)
    # cursellers = app.db.execute('''
    # SELECT Users.id, Users.firstname, Users.lastname, Inventory.quantity, Products.product_price
    # FROM Inventory
    # JOIN Users ON Inventory.seller_key = Users.id
    # JOIN Products ON Inventory.product_key = Products.product_key AND Inventory.seller_key = Products.seller_key
    # WHERE Inventory.product_key = :product_key and Users.is_seller = true
    # ''', product_key=product_key)
    
    cursellers = app.db.execute('''
        WITH temp as 
        (
            SELECT Products.seller_key as sk, Products.product_key as pk, Products.product_price as pp from Products where Products.product_name = 
            (
                SELECT Products.product_name
                From Products
                Where Products.product_key = :product_key
            )
        )
        SELECT Users.id,Users.firstname,Users.lastname, Inventory.quantity, temp.pp
        FROM Users
        JOIN temp on temp.sk = Users.id
        JOIN Inventory on Inventory.product_key = temp.pk
        ''', product_key=product_key)
    n = len(cursellers)
    curpage = request.args.get('curpage', type=int, default=1)
    per_page = 2
    totalpage = math.ceil(n/per_page)
    offset = (curpage - 1) * per_page
    cursellerPage = app.db.execute(f'''
        WITH temp as 
        (
            SELECT Products.seller_key as sk, Products.product_key as pk, Products.product_price as pp from Products where Products.product_name = 
            (
                SELECT Products.product_name
                From Products
                Where Products.product_key = :product_key
            )
        )
        SELECT Users.id,Users.firstname,Users.lastname, Inventory.quantity, temp.pp
        FROM Users
        JOIN temp on temp.sk = Users.id
        JOIN Inventory on Inventory.product_key = temp.pk
        LIMIT {per_page} OFFSET {offset}

        ''', product_key=product_key)
    curreviews = app.db.execute('''
    SELECT Users.firstname, Users.lastname, ProductReviews.prod_review_id, ProductReviews.review_rating, ProductReviews.review_description, ProductReviews.product_key
    FROM ProductReviews
    JOIN Users ON ProductReviews.person_reviewing_id = Users.id
    WHERE ProductReviews.product_key = :product_key
    ''', product_key=product_key)

    nr = len(curreviews)
    curpagereview = request.args.get('curpagereview', type=int, default=1)
    per_page_review = 3
    totalpagereview = math.ceil(nr/per_page_review)
    offsetreview = (curpagereview - 1) * per_page_review
    reviewsPage = app.db.execute(f'''
    SELECT Users.firstname, Users.lastname, ProductReviews.prod_review_id, ProductReviews.review_rating, ProductReviews.review_description, ProductReviews.product_key
    FROM ProductReviews
    JOIN Users ON ProductReviews.person_reviewing_id = Users.id
    WHERE ProductReviews.product_key = :product_key
    LIMIT {per_page_review} OFFSET {offsetreview}
    ''', product_key=product_key)
    avgreview = app.db.execute(
        '''
    SELECT round(avg(review_rating), 2), count(*) from ProductReviews
    where product_key = :product_key group by product_key
    ''', product_key=product_key
    )
    # avgreview = app.db.execute(
    #     '''
    # SELECT round(avg(review_rating), 2), count(*) from ProductReviews
    # where product_key = :product_key group by product_key
    # ''', product_key=product_key
    # )
    category = app.db.execute(
        '''
    SELECT Product_Category.cat_key, cat_name from Product_Category inner join Products on Products.cat_key = Product_Category.cat_key 
    where product_key = :product_key 
    ''', product_key=product_key
    )
    if not avgreview:
        avgreview = [5,0]
    else:
        avgreview = avgreview[0]
    return render_template('curproduct.html',
                            selected_product = prods,
                            sellers_stock = cursellerPage,
                            selected_reviews = reviewsPage,
                            avgreview = avgreview,
                            category = category,
                            curpage = curpage,
                            totalpage = totalpage,
                            curpagereview = curpagereview,
                            totalpagereview = totalpagereview
                            )

@bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_key = request.form.get('product_key', type=int)
    seller_key = request.form.get('seller_id', type=int)
    quantity = request.form.get('quantity', type=int)
    discount = request.form.get('discount_code', type=int)
    product_name = app.db.execute('''
    SELECT Products.product_name from Products where Products.product_key = :product_key''', product_key = product_key)
    product_name = product_name[0][0]
    pkey = app.db.execute('''Select Products.Product_key, Products.product_discount_code
    FROM Products 
    WHERE Products.seller_key = :seller_key and Products.product_name = :product_name''', seller_key = seller_key, product_name = product_name)
    pkey,discode = pkey[0][0], pkey[0][1]
    tosub = 1
    if discount and discount == discode:
        x = app.db.execute('''
        SELECT Discounts.discount_amount
        FROM Discounts
        WHERE Discounts.discount_key = :discount_key 
    ''', discount_key = discount)
        if x:
            tosub = x[0][0]/100
    price = float(request.form.get('price1'))
    total_price = float(quantity)*float(price)*float(tosub)
    total_price = round(total_price,2)
    buyer_key = current_user.id
    with app.db.engine.begin() as conn:
        conn.execute(text('''INSERT INTO Cart (buyer_key, product_key, seller_key, quantity,price,total_price)
        VALUES (:buyer_key, :product_key, :seller_key, :quantity, :price, :total_price)'''),
        {"buyer_key": buyer_key, "product_key": pkey, "seller_key": seller_key, "quantity": quantity, "price": price, "total_price": total_price})
        conn.commit()
    # app.db.execute('''
    #     INSERT INTO Cart (buyer_key, product_key, seller_key, quantity,price,total_price)
    #     VALUES (:buyer_key, :product_key, :seller_key, :quantity, :price, :total_price)
    # ''', buyer_key=buyer_key, product_key=pkey, seller_key = seller_key, quantity=quantity, price = price, total_price = total_price)
    return redirect(url_for('products.search_product'))
    # return redirect(url_for('products.curproduct', product_key=product_key))