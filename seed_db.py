import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product

# Create initial customers and products
customers = [
    Customer.objects.create(name="Seed Customer 1", email="seed1@example.com", phone="+1234567890"),
    Customer.objects.create(name="Seed Customer 2", email="seed2@example.com"),
]
products = [
    Product.objects.create(name="Seed Laptop", price=999.99, stock=5),
    Product.objects.create(name="Seed Mouse", price=29.99, stock=20),
]

print("Seeded data successfully!")