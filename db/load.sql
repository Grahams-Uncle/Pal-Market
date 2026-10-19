-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:

-- All possible zipcode should be included, no auto-gen
\COPY Zipcode FROM 'Zipcode.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Address_Table FROM 'Address.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.address_table_address_key_seq',
                         (SELECT MAX(address_key)+1 FROM Address_Table),
                         false);

\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Product_Category FROM 'Category.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Discounts FROM 'Discounts.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.discounts_discount_key_seq',
                         (SELECT MAX(discount_key)+1 FROM Discounts),
                         false);

\COPY Products FROM 'Products.csv' WITH (FORMAT CSV, DELIMITER ',', NULL '', FORCE_NULL(product_discount_code))
SELECT pg_catalog.setval('public.products_product_key_seq',
                         (SELECT MAX(product_key)+1 FROM Products),
                         false);

\COPY ProductReviews FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.productReviews_prod_review_id_seq',
                         (SELECT MAX(prod_review_id)+1 FROM ProductReviews),
                         false);

\COPY UserReviews FROM 'UserReviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.userReviews_user_review_id_seq',
                         (SELECT MAX(user_review_id)+1 FROM UserReviews),
                         false);

\COPY OrderHistory FROM 'Purchases.csv' WITH (FORMAT CSV, DELIMITER ',', NULL '', FORCE_NULL(prod_review_id,fulfillment_time, user_review_id))
SELECT pg_catalog.setval('public.orderHistory_order_id_seq',
                         (SELECT MAX(order_id)+1 FROM OrderHistory),
                         false);

\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.Cart_cart_item_id_seq',
                         (SELECT MAX(cart_item_id)+1 FROM Cart),
                         false);


