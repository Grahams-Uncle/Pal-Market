from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

num_users = 100
num_products = 1500
num_purchases = 2500
num_addresses = 200
num_zipcodes = 50
num_categories = 23
num_discounts = 20
num_reviews = 1000
#num_packages = 500

Faker.seed(0)
random.seed(42)
fake = Faker()

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_users(num_users):
    with open('Users_unhashed.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        # writer.writerow(['id', 'email', 'password', 'user_ship_address', 'user_bill_address', 'user_balance', 'user_rating', 'user_bio', 'is_seller', 'firstname', 'lastname'])
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = fake.password(length=8)
            # password = generate_password_hash(plain_password)
            password = plain_password
            user_ship_address = fake.random_int(min=0, max=num_addresses-1)
            user_bill_address = fake.random_int(min=0, max=num_addresses-1)
            user_balance = f'{str(fake.random_int(max=1000))}.{fake.random_int(max=99):02}'
            user_bio = fake.sentence(nb_words=10)
            is_seller = fake.boolean(chance_of_getting_true=25)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            writer.writerow([uid, email, password, user_ship_address, user_bill_address, user_balance, user_bio, is_seller, firstname, lastname])

        print(f'{num_users} generated')

    with open('Users_unhashed.csv', 'r') as file:
            reader = csv.reader(file)
            with open('Users.csv', 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                for row in reader:
                    row[2] = generate_password_hash(row[2])
                    writer.writerow(row)

def gen_products(num_products):
    names = ["Lamball", "Cattiva", "Chikipi", "Lifmunk", "Foxparks", "Fuack", "Sparkit", "Tanzee", "Rooby", "Pengullet", 
    "Penking","Jolthog", "Jolthog Cryst", "Gumoss", "Vixy", "Hoocrates", "Teafant", "Depresso", "Cremis", "Daedream", "Rushoar", 
    "Nox", "Fuddler", "Killamari", "Mau", "Mau Cryst", "Celaray", "Direhowl", "Tocotoco", "Flopie", "Mozzarina", "Bristla", "Gobfin", "Gobfin Ignis",
    "Hangyu", "Hangyu Cryst", "Mossanda", "Woolipop", "Caprity", "Melpaca", "Eikthyrdeer", "Eikthyrdeer Terra", "Nitewing", "Ribbuny", "Incineram", "Cinnamoth", "Arsox",
    "Dumud", "Cawgnito", "Leezpunk", "Loupmoon", "Galeclaw", "Robinquill", "Robinquill Terra", "Gorirat", "Beegarde", "Elizabee", "Grintale", "Swee",
    "Sweepa", "Chillet", "Univolt", "Pyrin", "Pyrin Noct", "Reindrix", "Rayhound", "Kitsun", "Dazzi", "Lunaris", "Dinossom",
    "Surfent", "Maraith", "Digtoise", "Tombat", "Lovander", "Flambelle", "Vanwyrm", "Vanwyrm Cryst", "Bushi", "Beakon", "Ragnahawk", "Katress", 
    "Wixen", "Verdash", "Vaelet", "Sibelyx", "Elphidran", "Kelpsea", "Kelpsea Ignis", "Azurobe", "Cryolinx", "Blazehowl", "Relaxaurus", "Broncherry",
    "Petallia", "Reptyro", "Reptyro Cryst", "Kingpaca", "Kingpaca Cryst", "Mammorest", "Mammorest Cryst", "Wumpo", "Wumpo Botan", "Warsect", "Fenglope", "Felbat", "Quivern", "Blazamut", "Blazehowl Noct", "Helzephyr", "Astegon",
    "Menasting", "Anubis", "Jormuntide", "Jormuntide Ignis", "Suzaku", "Grizzbolt", "Lyleen", "Lyleen Noct", "Faleris", "Orserk", "Shadowbeak", "Paladius", "Necromus",
    "Frostallion", "Jetragon", "Bellanoir"
    ]
    available_pids = []
    sellers = []
    with open('Users.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[7] == 'True':
                sellers.append(int(row[0])) 
    element_key = {}
    with open('Category.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            element_key[row[1].strip().replace("'", "")] = row[0]
    element_map = {}
    with open('pal_element.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            element_map[row[0]]=element_key[row[1]]

    with open('Products.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        # writer.writerow(['product_key', 'seller_key', 'cat_key', 'product_name', 'product_description', 'product_price', 'product_image', 'product_discount_code', 'available', 'product_rating']) 
        sellers_prod = {seller: names.copy() for seller in sellers} # Ensure product can only post each product once
        discount_code_counter = 0
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            if len(sellers)==0:
                print(f'Finished', end=' ', flush=True)
                break
            seller_key = random.choice(sellers)
            while len(sellers_prod[seller_key])==0:
                seller_key = random.choice(sellers)
            item = random.randrange(len(sellers_prod[seller_key]))
            name = sellers_prod[seller_key].pop(item) # Ensure product can only post each product once
            cat_key = element_map[name]
            if len(sellers_prod[seller_key])==0:
                sellers.remove(seller_key)
            description = fake.sentence(nb_words=10)
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            image = f"/image/{name}.png"
            if fake.boolean(chance_of_getting_true=60):
                discount_code = discount_code_counter
                discount_code_counter += 1
            else:
                discount_code = None
            available = fake.boolean(chance_of_getting_true=80)
            rating = f'{fake.random_int(min=0, max=4)}.{fake.random_int(max=9)}'
            if available:
                available_pids.append((pid,seller_key))
            writer.writerow([pid, seller_key, cat_key, name, description, price, image, discount_code, available, rating])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

def gen_addresses(num_addresses):
    zipcodes = []
    address = []
    with open('Zipcode.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            zipcodes.append(int(row[0]))  
    with open('Users.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            address.append(int(row[3]))  
            address.append(int(row[4]))  
    address = list(set(address))
    with open('Address.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Addresses...', end=' ', flush=True)
        # writer.writerow(['address_key', 'street_num', 'street_name', 'zipcode'])
        for id in address:
            if id == address[-1]:
                print(f'{id}', end=' ', flush=True)
            street_num = fake.building_number()
            street_name = fake.street_name()
            zipcode = random.choice(zipcodes)
            writer.writerow([id, street_num, street_name, zipcode])
        print(f'{num_addresses} generated')

def gen_categories(num_categories):
    with open('Category.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Categories...', end=' ', flush=True)
        # writer.writerow(['cat_key', 'cat_name'])
        for id in range(num_categories):
            if id % 10 == 0:
                print(f'{id}', end=' ', flush=True)
            name = fake.word()
            writer.writerow([id, name])
        print(f'{num_categories} generated')

def gen_discounts(num_discounts):
    discount_codes = []
    with open('Products.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[7]:
                discount_codes.append(int(row[7]))  
    discount_amounts = [i / 100 for i in range(5,96,5)]
    with open('Discounts.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Discounts...', end=' ', flush=True)
        # writer.writerow(['discount_key', 'discount_amount'])
        for i in range(len(discount_codes)):
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            discount_code = discount_codes[i]
            discount_amount = fake.random_element(elements=discount_amounts)
            writer.writerow([discount_code, discount_amount])
        print(f'{len(discount_codes)} generated')


    with open('UserReviews.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('User Reviews...', end=' ', flush=True)
        # writer.writerow(['user_review_id', 'person_key', 'person_reviewing_id', 'review_rating', 'review_description', 'review_image'])
        for id in range(num_reviews):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            person_key = fake.random_int(min=0, max=num_users-1)
            person_reviewing_id = fake.random_int(min=0, max=num_users-1)
            review_rating = f'{fake.random_int(min=0, max=4)}.{fake.random_int(max=9)}'
            review_description = fake.sentence(nb_words=10)
            review_image = fake.image_url()
            writer.writerow([id, person_key, person_reviewing_id, review_rating, review_description, review_image])
        print(f'{num_reviews} generated')


def gen_purchases(num_purchases, num_users, available_pids, num_reviews):
    with open('Purchases.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Generating Purchases...', end=' ', flush=True)       
        gen_prod_reviews = 0
        gen_user_reviews = 0
        for order_id in range(num_purchases):
            if order_id % 100 == 0:
                    print(f'{order_id}', end=' ', flush=True)

            num_products_per_order = fake.random_int(min=1, max=5)  
            buyer_key = fake.random_int(min=1, max=num_users-1)
            used_product_keys = set()  
            order_time = fake.date_time_between(start_date='-1y', end_date='now')
            for _ in range(num_products_per_order):
                               
                product_key, seller_key = fake.random_element(elements=[pid for pid in available_pids if pid[0] not in used_product_keys])
                while buyer_key == seller_key:
                    buyer_key = fake.random_int(min=1, max=num_users-1)
                
                used_product_keys.add(product_key)  
                
                order_quantity = fake.random_int(min=1, max=10)
                is_fulfilled = fake.boolean(chance_of_getting_true=80)
                if is_fulfilled:
                    fulfillment_time = fake.date_time_between(start_date=order_time, end_date='now')
                else:
                    fulfillment_time = None 
                # prod_review_id = fake.random_int(min=1, max=num_reviews-1) if fake.boolean(chance_of_getting_true=30) else None
                if fake.boolean(chance_of_getting_true=80) and is_fulfilled:
                    prod_review_id = gen_prod_reviews
                    gen_prod_reviews += 1
                else:
                    prod_review_id = None
                if fake.boolean(chance_of_getting_true=80) and is_fulfilled:
                    user_review_id = gen_user_reviews
                    gen_user_reviews += 1
                else:
                    user_review_id = None
                writer.writerow([order_id, buyer_key, seller_key, product_key, order_quantity, is_fulfilled, fulfillment_time, order_time, prod_review_id, user_review_id])
        
        print(f'\n{num_purchases} Unique Order IDs Generated, with multiple products per order.')

    
def gen_prod_reviews(num_reviews, num_users, available_pids):
    orders = []
    with open('Purchases.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                orders.append((row[8],row[1],row[2],row[3]))
    product_key_to_image = {}
    with open('Products.csv', 'r') as f:
        products_reader = csv.reader(f)
        for product in products_reader:
            product_key_to_image[product[0]] = (product[3], product[6])  # product_key to (product_name, image_path)
    with open('ProductReviews.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Product Reviews...', end=' ', flush=True)        
        for i in range(len(orders)):
            if i % 100 == 0:
                print(f'{i}', end=' ', flush=True)
            if orders[i][0]:
                prod_review_id, person_reviewing_id, seller_key, product_key = orders[i]
                review_rating = f'{fake.random_int(min=0, max=4)}.{fake.random_int(max=9)}'
                review_description = fake.sentence(nb_words=10)
                # Retrieve the image path using the product key
                product_name, image_path = product_key_to_image.get(product_key, ("Unknown", "/image/default.png"))
                review_image = f"{image_path}"
                writer.writerow([prod_review_id, product_key, seller_key, person_reviewing_id, review_rating, review_description, review_image])
        print(f'{num_reviews} generated')

def gen_user_reviews(num_reviews, num_users, available_pids):
    orders = []
    with open('Purchases.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                orders.append((row[9],row[1],row[2]))
    product_key_to_image = {}
    with open('Products.csv', 'r') as f:
        products_reader = csv.reader(f)
        for product in products_reader:
            product_key_to_image[product[0]] = (product[3], product[6])  # product_key to (product_name, image_path)
    with open('UserReviews.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('User Reviews...', end=' ', flush=True)
        for i in range(len(orders)):
            if i % 100 == 0:
                print(f'{i}', end=' ', flush=True)
            if orders[i][0]:
                user_review_id, person_reviewing_id, person_key = orders[i]
                review_rating = f'{fake.random_int(min=0, max=4)}.{fake.random_int(max=9)}'
                review_description = fake.sentence(nb_words=10)
                review_image = fake.image_url()
                writer.writerow([user_review_id, person_key, person_reviewing_id, review_rating, review_description, review_image])
        print(f'{num_reviews} generated') 

'''
def gen_purchases(num_purchases, num_users, available_pids):
    orders_data = []
    with open('Purchases.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        # writer.writerow(['order_id', 'buyer_key', 'seller_key', 'product_key', 'order_quantity', 'is_fulfilled', 'order_time', 'prod_review_id'])
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            buyer_key = fake.random_int(min=0, max=num_users-1)
            product_key, seller_key = fake.random_element(elements=available_pids)
            while buyer_key == seller_key:
                buyer_key = fake.random_int(min=1, max=num_users)
            order_quantity = fake.random_int(min=1, max=10)
            is_fulfilled = fake.boolean(chance_of_getting_true=80)
            order_time = fake.date_time_between(start_date='-1y', end_date='now')
            if is_fulfilled:
                fulfillment_time = fake.date_time_between(start_date=order_time, end_date='now')
            else:
                fulfillment_time = None 
            prod_review_id = fake.random_int(min=1, max=num_reviews) if fake.boolean(chance_of_getting_true=30) else ''  
            writer.writerow([id, buyer_key, seller_key, product_key, order_quantity, is_fulfilled, fulfillment_time, order_time, prod_review_id])
            orders_data.append({
                'order_id': id,
                'buyer_id': buyer_key,
                'is_fulfilled': is_fulfilled,
                'fulfillment_time': fulfillment_time
            })
        print(f'{num_purchases} generated')
    return orders_data

def gen_OrderPackage(num_packages, orders_data):
    with open('OrderPackage.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Generating Order Packages...', end=' ')
        
        buyer_orders = {}
        for order in orders_data:
            if order['buyer_id'] not in buyer_orders:
                buyer_orders[order['buyer_id']] = []
            buyer_orders[order['buyer_id']].append(order)

        used_orders = set()
        all_order_ids = {order['order_id'] for order in orders_data}
        package_id = 0

        for buyer_id, orders in buyer_orders.items():
            while orders:
                num_orders_in_package = fake.random_int(min=1, max=len(orders))
                package_orders = fake.random_elements(elements=orders, length=num_orders_in_package, unique=True)
                
                #all_fulfilled = all(order['is_fulfilled'] for order in package_orders)
                #latest_fulfillment_time = max((order['fulfillment_time'] for order in package_orders if order['fulfillment_time']), default=None)
                #is_fulfilled = all_fulfilled and latest_fulfillment_time is not None
                #fulfillment_time = latest_fulfillment_time if is_fulfilled else None
                
                for order in package_orders:
                    writer.writerow([package_id, order['order_id']])
                    used_orders.add(order['order_id'])
                    orders.remove(order)  
                
                package_id += 1

        unused_orders = all_order_ids - used_orders
        for order_id in unused_orders:
            order = next(order for order in orders_data if order['order_id'] == order_id)
            writer.writerow([package_id, order['order_id']])
            package_id += 1

        print(f'{num_packages} packages generated.')
'''

def gen_cart_items(num_purchases, num_users, available_pids):
    with open('Cart.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Cart Items...', end=' ', flush=True)
        # writer.writerow(['cart_id', 'buyer_key', 'product_key', 'seller_key', 'quantity', 'price', 'total_price', 'added_to_cart_time'])
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            buyer_key = fake.random_int(min=0, max=num_users-1)
            product_key, seller_key = fake.random_element(elements=available_pids)
            while buyer_key == seller_key:
                buyer_key = fake.random_int(min=0, max=num_users-1)
            quantity = fake.random_int(min=1, max=10)
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            total_price = f'{str(fake.random_int(max=5000))}.{fake.random_int(max=99):02}'
            added_to_cart_time = fake.date_time_between(start_date='-1y', end_date='now')
            writer.writerow([id, buyer_key, product_key, seller_key, quantity, price, total_price, added_to_cart_time])
        print(f'{num_purchases} generated')

def gen_inventory(available_pids, num_users):
    sellers_product = []
    with open('Inventory.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        # writer.writerow(['product_key', 'seller_key', 'quantity'])
        for pid, seller in available_pids:
            seller_key = seller
            quantity = fake.random_int(min=0, max=100)
            writer.writerow([pid, seller_key, quantity])
        print(f'{len(available_pids)} generated')

gen_users(num_users)
gen_addresses(num_addresses)

available_pids = gen_products(num_products)
gen_discounts(num_discounts)
gen_purchases(num_purchases, num_users, available_pids, num_reviews)
gen_prod_reviews(num_reviews, num_users, available_pids)
gen_user_reviews(num_reviews, num_users, available_pids)

#orders = gen_purchases(num_purchases, num_users, available_pids)
gen_cart_items(num_purchases, num_users, available_pids)
gen_inventory(available_pids, num_users)
#gen_OrderPackage(num_packages, orders)
