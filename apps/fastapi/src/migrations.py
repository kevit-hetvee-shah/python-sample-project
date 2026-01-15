import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from apps.fastapi.src.models import Base, engine, Product, User, Cart, Company, Category, SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def run_migrations():
    """Create all tables in the database."""
    print("Running database migrations...")
    Base.metadata.create_all(bind=engine)
    print("Migrations completed successfully!")


def seed_dummy_data():
    """Seed dummy categories, companies, products and users into the database."""
    print("Seeding dummy data...")
    db = SessionLocal()

    # Check if data already exists
    existing_categories = db.query(Category).count()
    existing_companies = db.query(Company).count()
    existing_products = db.query(Product).count()
    existing_users = db.query(User).count()
    if existing_categories > 0 or existing_companies > 0 or existing_products > 0 or existing_users > 0:
        print(f"Database already has data (categories: {existing_categories}, companies: {existing_companies}, users: {existing_users}, products: {existing_products}). Skipping seed.")
        db.close()
        return

    # Generate 50 categories
    category_names = [
        "Audio", "Wearables", "Power & Charging", "Gaming", "Monitors", "Accessories",
        "Laptops", "Smartphones", "Tablets", "Cameras", "Drones", "Smart Home",
        "Networking", "Storage", "Software", "Security", "Home Entertainment", "TVs",
        "Projectors", "Printers", "Scanners", "Ink & Toner", "Cables", "Desk",
        "Office Chairs", "Webcams", "Microphones", "Headphones", "Earbuds", "Speakers",
        "Keyboards", "Mice", "Mouse Pads", "Graphics Cards", "Processors", "Memory",
        "SSDs", "HDDs", "Cooling", "Cases", "Motherboards", "Power Supplies", "VR",
        "AR", "Car Tech", "GPS", "Fitness", "Health", "Outdoor", "Kids Tech"
    ]
    dummy_categories = [
        Category(name=name, description=f"{name} products and accessories")
        for name in category_names
    ]

    # Generate 30 companies
    company_data = [
        ("TechGadgets Inc", "Leading electronics manufacturer", "https://techgadgets.com"),
        ("AudioPro Solutions", "Professional audio equipment", "https://audiopro.com"),
        ("FitLife Electronics", "Fitness and wellness technology", "https://fitlife.com"),
        ("GamerZone", "Gaming peripherals and accessories", "https://gamerzone.com"),
        ("Office Essentials", "Office and productivity products", "https://officeessentials.com"),
        ("Digital Dreams", "Digital imaging and photography", "https://digitaldreams.com"),
        ("ConnectAll", "Networking and connectivity solutions", "https://connectall.com"),
        ("SecureTech", "Security and surveillance products", "https://securetech.com"),
        ("SmartHome Hub", "Home automation and smart devices", "https://smarthomehub.com"),
        ("VisionPro", "Display and monitor technology", "https://visionpro.com"),
        ("PowerMax", "Power and charging solutions", "https://powermax.com"),
        ("DataVault", "Data storage and backup solutions", "https://datavault.com"),
        ("GameMaster", "Premium gaming equipment", "https://gamemaster.com"),
        ("MobileTech", "Mobile accessories and gadgets", "https://mobiletech.com"),
        ("CloudSync", "Cloud storage and sync services", "https://cloudsync.com"),
        ("AudioBliss", "High-fidelity audio equipment", "https://audiobliss.com"),
        ("Visionary", "VR and AR technology", "https://visionary.com"),
        ("GreenEnergy", "Eco-friendly tech products", "https://greenenergy.com"),
        ("CreativePro", "Creative software and hardware", "https://creativepro.com"),
        ("AutoTech", "Automotive electronics", "https://autotech.com"),
        ("HealthTech", "Health monitoring devices", "https://healthtech.com"),
        ("EduTech", "Educational technology products", "https://edutech.com"),
        ("KidTech", "Technology for children", "https://kidtech.com"),
        ("OutdoorPro", "Outdoor and adventure tech", "https://outdoorpro.com"),
        ("StreamerPro", "Streaming and content creation", "https://streamerpro.com"),
        ("CodeMaster", "Developer tools and hardware", "https://codemaster.com"),
        ("DesignHub", "Design and creative tools", "https://designhub.com"),
        ("MusicTech", "Music production equipment", "https://musictech.com"),
        ("PhotoPro", "Photography equipment", "https://photopro.com"),
        ("TravelTech", "Travel and navigation gadgets", "https://traveltech.com"),
    ]
    dummy_companies = [
        Company(name=name, description=description, website_url=website, logo_url=f"https://example.com/logos/{name.lower().replace(' ', '_')}.png")
        for name, description, website in company_data
    ]

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

    # First add categories and companies so we can reference their IDs
    try:
        db.add_all(dummy_categories)
        db.add_all(dummy_companies)
        db.flush()  # Flush to get the IDs without committing

        # Generate 100 products with diverse combinations
        product_templates = [
            ("Wireless Bluetooth Headphones", 79.99, "Premium noise-cancelling wireless headphones with 30-hour battery life"),
            ("Smart Fitness Watch", 199.99, "Track your health metrics with this advanced fitness smartwatch"),
            ("Portable Power Bank 20000mAh", 49.99, "High capacity power bank with fast charging support"),
            ("Mechanical Gaming Keyboard", 129.99, "RGB mechanical keyboard with customizable switches"),
            ("4K Ultra HD Monitor 27-inch", 349.99, "Crystal clear 4K display with HDR support"),
            ("Wireless Gaming Mouse", 59.99, "Precision gaming mouse with customizable DPI settings"),
            ("USB-C Hub Multiport Adapter", 39.99, "7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader"),
            ("Laptop Stand Aluminum", 29.99, "Ergonomic adjustable laptop stand for better posture"),
            ("Webcam HD 1080p", 69.99, "Full HD webcam with auto-focus and built-in microphone"),
            ("Wireless Charging Pad", 24.99, "Fast wireless charging pad compatible with all Qi devices"),
        ]

        colors = ["Black", "White", "Silver", "Space Gray", "Rose Gold", "Blue", "Red", "RGB", "Carbon Fiber", "Midnight Green"]
        discounts = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]

        dummy_products = []
        for i in range(100):
            template_idx = i % len(product_templates)
            base_name, base_price, base_desc = product_templates[template_idx]
            category_idx = i % len(dummy_categories)
            company_idx = i % len(dummy_companies)
            color_idx = i % len(colors)
            discount_idx = i % len(discounts)

            product = Product(
                name=f"{base_name} - Edition {i + 1}" if i >= 10 else base_name,
                price=round(base_price + (i % 50) * 1.5, 2),
                description=base_desc,
                image_url=f"https://example.com/images/product_{i + 1}.jpg",
                detail_description=f"{base_desc}. This premium edition includes enhanced features and improved performance.",
                discount=discounts[discount_idx],
                category_id=dummy_categories[category_idx].id,
                company_id=dummy_companies[company_idx].id,
                color=colors[color_idx],
                extra_images=[f"https://example.com/images/product_{i + 1}_2.jpg", f"https://example.com/images/product_{i + 1}_3.jpg"]
            )
            dummy_products.append(product)

        db.add_all(dummy_users)
        db.add_all(dummy_products)
        db.commit()
        print(f"Successfully seeded {len(dummy_categories)} categories, {len(dummy_companies)} companies, {len(dummy_users)} users and {len(dummy_products)} products!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_migrations()
    seed_dummy_data()
