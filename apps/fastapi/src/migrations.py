import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from apps.fastapi.src.models import Base, engine, Product, User, SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def run_migrations():
    """Create all tables in the database."""
    print("Running database migrations...")
    Base.metadata.create_all(bind=engine)
    print("Migrations completed successfully!")


def seed_dummy_data():
    """Seed 10 dummy products and 5 dummy users into the database."""
    print("Seeding dummy product and user data...")
    db = SessionLocal()

    # Check if data already exists
    existing_products = db.query(Product).count()
    existing_users = db.query(User).count()
    if existing_products > 0 or existing_users > 0:
        print(f"Database already has data (users: {existing_users}, products: {existing_products}). Skipping seed.")
        db.close()
        return

    # Dummy users with raw passwords (for testing)
    dummy_users_data = [
        {"username": "john_doe", "password": "Password123!", "city": "New York", "state": "NY", "landmark": "Times Square"},
        {"username": "jane_smith", "password": "SecurePass456", "city": "Los Angeles", "state": "CA", "landmark": "Hollywood Sign"},
        {"username": "bob_wilson", "password": "MyP@ss789", "city": "Chicago", "state": "IL", "landmark": "Millennium Park"},
        {"username": "alice_brown", "password": "Alice2024!", "city": "Houston", "state": "TX", "landmark": None},
        {"username": "charlie_davis", "password": "Charlie@123", "city": "Phoenix", "state": "AZ", "landmark": "Desert Botanical Garden"},
    ]

    dummy_users = []
    for user_data in dummy_users_data:
        dummy_users.append(User(
            username=user_data["username"],
            password=pwd_context.hash(user_data["password"]),
            city=user_data["city"],
            state=user_data["state"],
            landmark=user_data["landmark"]
        ))

    dummy_products = [
        Product(
            name="Wireless Bluetooth Headphones",
            price=79.99,
            description="Premium noise-cancelling wireless headphones with 30-hour battery life",
            image_url="https://example.com/images/headphones.jpg"
        ),
        Product(
            name="Smart Fitness Watch",
            price=199.99,
            description="Track your health metrics with this advanced fitness smartwatch",
            image_url="https://example.com/images/smartwatch.jpg"
        ),
        Product(
            name="Portable Power Bank 20000mAh",
            price=49.99,
            description="High capacity power bank with fast charging support",
            image_url="https://example.com/images/powerbank.jpg"
        ),
        Product(
            name="Mechanical Gaming Keyboard",
            price=129.99,
            description="RGB mechanical keyboard with customizable switches",
            image_url="https://example.com/images/keyboard.jpg"
        ),
        Product(
            name="4K Ultra HD Monitor 27-inch",
            price=349.99,
            description="Crystal clear 4K display with HDR support",
            image_url="https://example.com/images/monitor.jpg"
        ),
        Product(
            name="Wireless Gaming Mouse",
            price=59.99,
            description="Precision gaming mouse with customizable DPI settings",
            image_url="https://example.com/images/mouse.jpg"
        ),
        Product(
            name="USB-C Hub Multiport Adapter",
            price=39.99,
            description="7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader",
            image_url="https://example.com/images/usbhub.jpg"
        ),
        Product(
            name="Laptop Stand Aluminum",
            price="29.99",
            description="Ergonomic adjustable laptop stand for better posture",
            image_url="https://example.com/images/laptopstand.jpg"
        ),
        Product(
            name="Webcam HD 1080p",
            price=69.99,
            description="Full HD webcam with auto-focus and built-in microphone",
            image_url="https://example.com/images/webcam.jpg"
        ),
        Product(
            name="Wireless Charging Pad",
            price=24.99,
            description="Fast wireless charging pad compatible with all Qi devices",
            image_url="https://example.com/images/charger.jpg"
        )
    ]

    try:
        db.add_all(dummy_users)
        db.add_all(dummy_products)
        db.commit()
        print(f"Successfully seeded {len(dummy_users)} users and {len(dummy_products)} products!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_migrations()
    seed_dummy_data()
