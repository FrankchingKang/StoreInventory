import csv
import re
import datetime
import sys
import os

from collections import OrderedDict
from peewee import *

def clear_screen():
  os.system("cls" if os.name == "nt" else "clear")



db = SqliteDatabase('Inventory.db')

class Inventory(Model):
    product_id = PrimaryKeyField()
    product_name = CharField(max_length = 255,unique = True)
    product_price = IntegerField(default=0)
    product_quantity = IntegerField(default=0)
    date_updated = DateField(default= datetime.datetime.now().date())

    class Meta:
        database = db

def initialize_database():
    """" connecting the database and create the table """
    db.connect()
    db.create_tables([Inventory], safe=True)



def read_data_from_file():
    """ reading the data from CSV file """
    with open('inventory.csv', newline = '') as csvfile:
        invreader = csv.DictReader(csvfile, delimiter = ',')
        product_list = []
        for row in invreader:
            # conver product_quantity to int
            row['product_quantity'] = int(row['product_quantity'])
            # conver product_price to int ($3.19 becomes 319, for example)
            price_i, price_f = re.match(r'^\$(?P<price_i>\d)\.(?P<price_f>\d\d)$',row['product_price']).groups()
            row['product_price'] = int(price_i+price_f)
            # conver date_updated to a date
            row['date_updated'] = datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y').date()
            product_list.append(row)
    return product_list

def add_data_to_DB(product_list):
    """ adding data to the database """
    for product in product_list:
        try:
            Inventory.create(
                product_name = product['product_name'],
                product_price = product['product_price'],
                product_quantity = product['product_quantity'],
                date_updated = product['date_updated'])
        except IntegrityError:
            product_record = Inventory.get(product_name=product['product_name'])
            if product_record.date_updated < product['date_updated']:
                product_record.product_price = product['product_price']
                product_record.product_name = product['product_name']
                product_record.product_quantity = product['product_quantity']
                product_record.date_updated = product['date_updated']
                product_record.save()

def view_ID_check(id):
    """ if user input a id is not in the data base, need a message be prompted """
    product_with_maxID = Inventory.select().order_by(Inventory.product_id.desc()).limit(1).get()
    if id > product_with_maxID.product_id:
        print("\t\nthis id is not exist! Please entrt again!\n")
        return False
    else:
        return True

def get_id():
    while True:
        try:
            id = input("Please inter the product id:").strip()
        except KeyboardInterrupt:
            action = input("\ndo you really want to exit? Y/N >")
            if action.upper() == "Y":
                os._exit(0)
        if re.match(r"\d", id) is None:
            print("\t\nit's not a value id!!\n")
        else:
            try:
                if view_ID_check(int(id)) is True:
                    return id
            except ValueError:
                print("\n\tit's no an value id. Please iput a number!\n")


def get_int_to_cents(int_price):
    i = int_price // 100
    f = int_price % 100
    if f < 10:
        return "${}.0{}".format(i,f)
    else:
        return "${}.{}".format(i,f)


def view_a_product():
    """ View a single product's inventory """
    id = get_id()
    detail =  Inventory.get(product_id = id)
    print("product name: {}".format(detail.product_name))
    print("product price: {}".format(get_int_to_cents(detail.product_price)))
    print("product quality: {}".format(detail.product_quantity))
    print("product date updated: {}\n".format(detail.date_updated))

def get_product_name():
    try:
        name = input("Please enter your product name:")
    except KeyboardInterrupt:
        action = input("\ndo you really want to exit? Y/N >")
        if action.upper() == "Y":
            os._exit(0)
    return name

def get_product_price():
    while True:
        try:
            price = input("Please enter your product price: $").strip()
        except KeyboardInterrupt:
            action = input("\ndo you really want to exit? Y/N >")
            if action.upper() == "Y":
                os._exit(0)
        try:
            float(price) # check whether a number
            price_i, price_f = re.match(r'^(?P<price_i>\d+)\.?(?P<price_f>\d+)?$',price).groups()
            if price_f is None: # int number
                print("\n\tPlease enter the cents. ex: 1.23\n")
            elif len(price_f) < 2:
                return int(price_i + price_f + "0")
            elif len(price_f) > 2:
                print("\n\tPlease only enter two decimal places\n")
            else:
                return int(price_i + price_f)


        except ValueError:
            print("Please input a value price number")
        except AttributeError:
            print("Please input a value price number")


def get_product_quantity():
    while True:
        try:
            quantity = int(input("Please enter your quantity:").strip())
            return quantity
        except KeyboardInterrupt:
            action = input("\ndo you really want to exit? Y/N >")
            if action.upper() == "Y":
                os._exit(0)
        except ValueError:
            print("Please input a int number")

def add_a_new_product():
    """ Add a new product to the database"""
    product = {}
    new_product_name = get_product_name()
    new_product_price = get_product_price()
    new_product_quantity = get_product_quantity()

    try:
        Inventory.create(
            product_name = new_product_name,
            product_price = new_product_price,
            product_quantity = new_product_quantity,
            date_updated = datetime.datetime.today().date())
    except IntegrityError:
        product_record = Inventory.get(product_name = new_product_name)
        if product_record.date_updated <= datetime.datetime.today().date():
            product_record.product_price = new_product_price
            product_record.product_name = new_product_name
            product_record.product_quantity = new_product_quantity
            product_record.date_updated = datetime.datetime.today().date()
            product_record.save()


def backup():
    """ Make a backup of the entire inventory """

    products = Inventory.select()
    with open('Inventory_backup.csv', 'w') as csvfile:
        inventory_fieldnames = ['product_name', 'product_price','product_quantity','date_updated']
        inventory_writer = csv.DictWriter(csvfile, fieldnames = inventory_fieldnames)

        inventory_writer.writeheader()
        for product in products:
            inventory_writer.writerow({
                'product_name': product.product_name,
                'product_price': get_int_to_cents(product.product_price),
                'product_quantity': product.product_quantity,
                'date_updated': product.date_updated
            })
    print("\n\tbackup successful!\n")



menu = OrderedDict([
        ('v', view_a_product),
        ('a', add_a_new_product),
        ('b', backup)
])

def manu_loop_enter_check(enter_char):
    """ check the enter char when user is selecting the action in manu loop """
    if enter_char not in menu and not "q":
        print("\n\tPlease enter v, a, or b\n")

def get_manu_action():
    """" get the action selection from user"""
    try:
        action = input("Please enter your action:").lower().strip()
    except KeyboardInterrupt:
        action = input("\ndo you really want to exit? Y/N >")
        if action.upper() == "Y":
            os._exit(0)
    return action


def manu_loop():
    """ showing the manu loop for use to interact """
    action = None
    while action != 'q':
        print('Enter q to exit.')
        for key, value in menu.items():
            print('{} {}'.format(key, value.__doc__)) # __doc__ will show the docstring of the function

        action = get_manu_action()
        manu_loop_enter_check(action)

        if action in menu:
            clear_screen()
            menu[action]()



if __name__ == '__main__':
    product_list = read_data_from_file()
    initialize_database()
    add_data_to_DB(product_list)
    manu_loop()
