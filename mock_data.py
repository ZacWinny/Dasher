import random
from faker import Faker
from werkzeug.security import generate_password_hash

from main import app
from website import db
from website.models import Restaurant, Customer, OrderItem, MenuItem, Order  # Adjust your import path

fake = Faker('en_AU')

food_categories = {
    "Italian": {
        "Pizza Margherita": "images/italian/pizza_margherita.jpg",
        "Spaghetti Carbonara": "images/italian/spaghetti_carbonara.jpg",
        "Lasagna": "images/italian/lasagna.jpg",
        "Tiramisu": "images/italian/tiramisu.jpg",
        "Panna Cotta": "images/italian/panna_cotta.jpg",
        "Caprese Salad": "images/italian/caprese_salad.jpg",
    },
    "Chinese": {
        "Fried Rice": "images/chinese/fried_rice.jpg",
        "General Tso's Chicken": "images/chinese/general_tsos_chicken.jpg",
        "Kung Pao Shrimp": "images/chinese/kung_pao_shrimp.jpg",
        "Egg Roll": "images/chinese/egg_roll.jpg",
        "Short Soup": "images/chinese/short_soup.jpg",
        "Sweet and Sour Pork": "images/chinese/sweet_and_sour_pork.jpg",
        "Dim Sum": "images/chinese/dim_sum.jpg",
        "Chow Mein": "images/chinese/chow_mein.jpg",
        "Peking Duck": "images/chinese/peking_duck.jpg",
    },
    "Thai": {
        "Pad Thai": "images/thai/pad_thai.jpg",
        "Green Curry": "images/thai/green_curry.jpg",
        "Tom Yum Soup": "images/thai/tom_yum_soup.jpg",
        "Massaman Curry": "images/thai/massaman_curry.jpg",
        "Pad See Ew": "images/thai/pad_see_ew.jpg",
        "Satay": "images/thai/satay.jpg",
    },
    "Indian": {
        "Butter Chicken": "images/indian/butter_chicken.jpg",
        "Tandoori Chicken": "images/indian/tandoori_chicken.jpg",
        "Samosa": "images/indian/samosa.jpg",
        "Naan Bread": "images/indian/naan_bread.jpg",
        "Chicken Tikka Masala": "images/indian/chicken_tikka_masala.jpg",
        "Rogan Josh": "images/indian/rogan_josh.jpg",
    },
    "Mexican": {
        "Tacos": "images/mexican/tacos.jpg",
        "Burrito": "images/mexican/burritos.jpg",
        "Enchilada": "images/mexican/enchiladas.jpg",
        "Quesadillas": "images/mexican/quesadillas.jpg",
        "Nachos": "images/mexican/nachos.jpg",
        "Churros": "images/mexican/churros.jpg",
    },
    "American": {
        "Hamburger": "images/american/hamburger.jpg",
        "Cheeseburger": "images/american/cheeseburger.jpg",
        "Hot Dog": "images/american/hot_dog.jpg",
        "Fries": "images/american/fries.jpg",
        "Fried Chicken": "images/american/fried_chicken.jpg",
        "Mac and Cheese": "images/american/mac_and_cheese.jpg",
        "BBQ Ribs": "images/american/bbq_ribs.jpg",
        "Caesar Salad": "images/american/caesar_salad.jpg",
    },
    "Japanese": {
        "Sushi": "images/japanese/sushi.jpg",
        "Ramen": "images/japanese/ramen.jpg",
        "Sashimi": "images/japanese/sashimi.jpg",
        "Tempura": "images/japanese/tempura.jpg",
        "Miso Soup": "images/japanese/miso_soup.jpg",
        "Donburi": "images/japanese/donburi.jpg",
    },
    "Greek": {
        "Souvlaki": "images/greek/souvlaki.jpg",
        "Spanakopita": "images/greek/spanakopita.jpg",
        "Baklava": "images/greek/baklava.jpg",
        "Greek Salad": "images/greek/greek_salad.jpg",
        "Hummus": "images/greek/hummus.jpg",
        "Falafel": "images/greek/falafel.jpg",
    },
    "Lebanese": {
        "Baba Ganoush": "images/lebanese/baba_ghanoush.jpg",
        "Falafel": "images/lebanese/falafel.jpg",
        "Shawarma": "images/lebanese/shawarma.jpg",
        "Fattoush Salad": "images/lebanese/fattoush_salad.jpg",
        "Kafta": "images/lebanese/kafta.jpg",
        "Baklava": "images/lebanese/baklava.jpg",
    },
    "Cafe": {
        "Latte": "images/cafe/latte.jpg",
        "Cappuccino": "images/cafe/cappuccino.jpg",
        "Espresso": "images/cafe/espresso.jpg",
        "Croissant": "images/cafe/croissant.jpg",
        "Muffin": "images/cafe/muffin.jpg",
        "Sandwich": "images/cafe/sandwich.jpg",
        "Salad": "images/cafe/salad.jpg",
        "Pastry": "images/cafe/pastry.jpg",
        "Smoothie": "images/cafe/smoothie.jpg",
    },
    "Club": {
        "Chicken Parmigiana": "images/club/chicken_parmigiana.jpg",
        "Steak Sandwich": "images/club/steak_sandwich.jpg",
        "Fish and Chips": "images/club/fish_and_chips.jpg",
        "Salt and Pepper Squid": "images/club/salt_and_pepper_squid.jpg",
        "Chicken Schnitzel": "images/club/chicken_schnitzel.jpg",
        "Garlic Bread": "images/club/garlic_bread.jpg",
    }
}


def generate_restaurants(num_restaurants):
    categories = ["Italian", "Chinese", "Thai", "Indian", "Mexican", "American", "Japanese", "Greek", "Lebanese",
                  "Cafe", "Club"]

    name_formats = {
        "Italian": ["{last_name}'s Ristorante", "Trattoria {last_name}", "Osteria {last_name}"],
        "Chinese": ["Golden Dragon", "Panda Express", "New China House", "China Garden"],
        "Thai": ["Thai Spice", "Bangkok Delight", "Pad Thai Palace", "Siam Bistro"],
        "Indian": ["Curry House", "Taste of India", "Delhi Diner", "Bombay Palace"],
        "Mexican": ["Tacos El {last_name}", "La Casa {last_name}", "Fiesta Mexicana"],
        "American": ["{last_name}'s Diner", "The Burger Joint", "BBQ Shack", "The Grill"],
        "Japanese": ["{last_name}'s Sushi Bar", "Tokyo Express", "Sushi Heaven", "Ramen Spot"],
        "Greek": ["{last_name}'s Taverna", "The Olive Branch", "Athens Grill", "Greek Delights"],
        "Lebanese": ["Beirut Bites", "Pita Paradise", "The Cedar Tree", "Flavors of Lebanon"],
        "Cafe": ["{last_name}'s Cafe", "The Daily Grind", "Coffee Corner", "Brewed Awakenings"],
        "Club": ["Club {last_name}", "The Velvet Lounge", "Neon Nights", "Electric Avenue"]
    }

    for _ in range(num_restaurants):
        category = random.choice(categories)
        name_format = random.choice(name_formats.get(category, ["{last_name}'s"]))
        name = name_format.format(last_name=fake.last_name())

        restaurant = Restaurant(
            email=fake.email(),
            password=fake.password(),
            name=name,
            category=category,
            address=fake.address(),
            type='restaurant'
        )
        db.session.add(restaurant)
    db.session.commit()


def generate_customers(num_customers):
    for _ in range(num_customers):
        customer = Customer(
            email=fake.email(),
            password=generate_password_hash(fake.password(), method='pbkdf2:sha256'),  # Hash the password
            name=fake.name(),
            address=fake.address(),
            membership=random.choice([True, False]),
            membership_type=random.choice(['monthly', 'annual']) if random.choice([True]) else None,
        )
        db.session.add(customer)
    db.session.commit()


def generate_menu_items(num_items_per_restaurant):
    restaurants = Restaurant.query.all()

    for restaurant in restaurants:
        item_names = set()

        for _ in range(num_items_per_restaurant):
            item_category = restaurant.category
            category_items = food_categories.get(item_category, [])

            while True:
                item_name = random.choice(list(
                    category_items.keys())) if category_items else fake.food_name()  # If category items are available, choose from keys
                if item_name not in item_names:
                    item_names.add(item_name)
                    break

            image_path = category_items.get(item_name, "/static/images/default_food.jpg")  # Get image path or default

            description = f"{fake.random_element(['Delicious', 'Mouthwatering', 'Authentic'])} {item_name}."
            price = round(
                random.uniform(8.0, 25.0) if item_category in ["Italian", "Chinese", "Thai"] else random.uniform(4.0,
                                                                                                                 12.0),
                2)

            menu_item = MenuItem(name=item_name, description=description, price=price, restaurant_id=restaurant.id,
                                 image_path=image_path)  # Use image_path from dictionary
            db.session.add(menu_item)

    db.session.commit()


def generate_orders(num_orders):
    customers = Customer.query.all()
    restaurants = Restaurant.query.all()
    status_options = ['Pending', 'Complete', 'Cancelled']
    service_options = ["Membership", "Pay-on-Demand"]

    for _ in range(num_orders):
        customer = random.choice(customers)
        restaurant = random.choice(restaurants)
        menu_items = random.sample(restaurant.menu_items.all(), random.randint(1, 5))
        order_items = [OrderItem(order_id=None, menu_item_id=item.id, quantity=random.randint(1, 3)) for item in
                       menu_items]

        menu_item_ids = [item.menu_item_id for item in order_items]
        menu_items = MenuItem.query.filter(MenuItem.id.in_(menu_item_ids)).all()
        menu_item_dict = {item.id: item for item in menu_items}
        total_price = sum([item.quantity * menu_item_dict[item.menu_item_id].price for item in order_items])

        order = Order(
            customer_id=customer.id,
            restaurant_id=restaurant.id,
            items=order_items,
            total_price=total_price,
            service_option=random.choice(service_options),
            status=random.choice(status_options)
        )
        db.session.add(order)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        generate_restaurants(10)
        generate_customers(20)
        generate_menu_items(6)
        generate_orders(20)
