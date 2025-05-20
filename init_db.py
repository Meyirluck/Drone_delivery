from app import create_app, db
from app.models import User, Restaurant, MenuItem

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()

        # Check if we already have data
        if Restaurant.query.first() is not None:
            print("Database already initialized.")
            return

        # Create restaurants
        restaurants = [
            Restaurant(
                name="KFC",
                description="Finger-lickin' good chicken and more!",
                logo_path="images/kfc-logo.png"
            ),
            Restaurant(
                name="Salam Bro",
                description="Authentic Middle Eastern cuisine with a modern twist.",
                logo_path="images/salam-bro-logo.png"
            ),
            Restaurant(
                name="YOLO Coffeehouse",
                description="Artisanal coffee and delicious pastries in a cozy atmosphere.",
                logo_path="images/yolo-logo.png"
            )
        ]

        for restaurant in restaurants:
            db.session.add(restaurant)
        db.session.commit()

        # Create menu items for KFC
        kfc = Restaurant.query.filter_by(name="KFC").first()
        kfc_items = [
            MenuItem(
                name="Original Recipe Chicken Bucket",
                description="8 pieces of our signature Original Recipe chicken",
                price=24.99,
                image_path="images/kfc-bucket.jpg",
                restaurant=kfc
            ),
            MenuItem(
                name="Zinger Burger",
                description="Crispy chicken fillet with lettuce and mayo",
                price=8.99,
                image_path="images/kfc-zinger.jpg",
                restaurant=kfc
            ),
            MenuItem(
                name="French Fries",
                description="Crispy golden fries",
                price=3.99,
                image_path="images/kfc-fries.jpg",
                restaurant=kfc
            )
        ]

        # Create menu items for Salam Bro
        salam = Restaurant.query.filter_by(name="Salam Bro").first()
        salam_items = [
            MenuItem(
                name="Shawarma Plate",
                description="Served with rice, salad, and garlic sauce",
                price=12.99,
                image_path="images/salam-shawarma.jpg",
                restaurant=salam
            ),
            MenuItem(
                name="Falafel Wrap",
                description="Crispy falafel with hummus and vegetables",
                price=9.99,
                image_path="images/salam-falafel.jpg",
                restaurant=salam
            ),
            MenuItem(
                name="Mixed Grill",
                description="Assortment of grilled meats with rice and salad",
                price=18.99,
                image_path="images/salam-mixed-grill.jpg",
                restaurant=salam
            )
        ]

        # Create menu items for YOLO Coffeehouse
        yolo = Restaurant.query.filter_by(name="YOLO Coffeehouse").first()
        yolo_items = [
            MenuItem(
                name="Artisan Coffee",
                description="Single-origin coffee beans, freshly roasted",
                price=4.99,
                image_path="images/yolo-coffee.jpg",
                restaurant=yolo
            ),
            MenuItem(
                name="Avocado Toast",
                description="Sourdough bread with avocado, poached eggs, and microgreens",
                price=8.99,
                image_path="images/yolo-avocado-toast.jpg",
                restaurant=yolo
            ),
            MenuItem(
                name="Chocolate Croissant",
                description="Buttery croissant filled with dark chocolate",
                price=3.99,
                image_path="images/yolo-croissant.jpg",
                restaurant=yolo
            )
        ]

        # Add all menu items
        for items in [kfc_items, salam_items, yolo_items]:
            for item in items:
                db.session.add(item)

        db.session.commit()
        print("Database initialized with sample data.")

if __name__ == "__main__":
    init_db() 