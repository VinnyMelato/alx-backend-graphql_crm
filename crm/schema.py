import graphene
from graphene import String, Decimal, List, Boolean, ID, Mutation, DateTime, InputObjectType
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from datetime import datetime

# Step 1: Define DjangoObjectTypes FIRST (before anything that uses them)
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "total_amount", "order_date")

    customer = graphene.Field(CustomerType)
    products = graphene.List(ProductType)  # Nested for orders

    def resolve_customer(self, info):
        return self.customer

    def resolve_products(self, info):
        return self.products.all()

# Step 2: InputTypes (used in Mutations)
class CustomerInput(InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

# Add this after CustomerInput and before the Mutation class

class CreateCustomer(Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = String()
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError("Email already exists")

            # Validate phone
            if input.phone and not re.match(r'^\+?\d{10,15}$|^\d{3}-\d{3}-\d{4}$', input.phone):
                raise ValidationError("Invalid phone format (e.g., +1234567890 or 123-456-7890)")

            customer = Customer.objects.create(**input)
            return CreateCustomer(customer=customer, message="Customer created successfully", success=True)
        except ValidationError as e:
            return CreateCustomer(message=str(e), success=False)
        except Exception as e:
            return CreateCustomer(message=f"Error: {str(e)}", success=False)

class OrderInput(InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Step 3: Mutations (from Tasks 1 & 2)
class CreateCustomer(Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = String()
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError("Email already exists")

            # Validate phone
            if input.phone and not re.match(r'^\+?\d{10,15}$$ |^\d{3}-\d{3}-\d{4} $$', input.phone):
                raise ValidationError("Invalid phone format (e.g., +1234567890 or 123-456-7890)")

            customer = Customer.objects.create(**input)
            return CreateCustomer(customer=customer, message="Customer created successfully", success=True)
        except ValidationError as e:
            return CreateCustomer(message=str(e), success=False)
        except Exception as e:
            return CreateCustomer(message=f"Error: {str(e)}", success=False)

class BulkCreateCustomers(Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(String)
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for data in input:
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        errors.append(f"Email {data.email} already exists")
                        continue
                    if data.phone and not re.match(r'^\+?\d{10,15}$$ |^\d{3}-\d{3}-\d{4} $$', data.phone):
                        errors.append(f"Invalid phone for {data.name}")
                        continue
                    cust = Customer.objects.create(**data)
                    created.append(cust)
                except Exception as e:
                    errors.append(f"Failed to create {data.name}: {str(e)}")
        return BulkCreateCustomers(customers=created, errors=errors, success=bool(created))

class CreateProduct(Mutation):
    class Arguments:
        name = String(required=True)
        price = Decimal(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)
    message = String()

    @classmethod
    def mutate(cls, root, info, name, price, stock):
        try:
            if price <= 0:
                raise ValidationError("Price must be positive")
            if stock < 0:
                raise ValidationError("Stock cannot be negative")
            product = Product.objects.create(name=name, price=price, stock=stock)
            return CreateProduct(product=product, message="Product created successfully")
        except ValidationError as e:
            return CreateProduct(message=str(e))
        except Exception as e:
            return CreateProduct(message=f"Error: {str(e)}")

class CreateOrder(Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = String()
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
            if not input.product_ids:
                raise ValidationError("At least one product required")
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                raise ValidationError("Invalid product ID(s)")
            order_date = input.order_date or datetime.now()
            order = Order.objects.create(customer=customer, order_date=order_date)
            order.products.set(products)
            order.save()  # Triggers total_amount calculation
            return CreateOrder(order=order, message="Order created successfully", success=True)
        except Customer.DoesNotExist:
            return CreateOrder(message="Customer not found", success=False)
        except Product.DoesNotExist:
            return CreateOrder(message="One or more products not found", success=False)
        except ValidationError as e:
            return CreateOrder(message=str(e), success=False)
        except Exception as e:
            return CreateOrder(message=f"Error: {str(e)}", success=False)

class UpdateLowStockProducts(Mutation):
    updated_products = List(ProductType)
    message = String()
    success = Boolean()

    @classmethod
    def mutate(cls, root, info):
        updated = []
        products = Product.objects.filter(stock__lt=10)
        for p in products:
            p.stock = p.stock + 10
            p.save()
            updated.append(p)
        return UpdateLowStockProducts(updated_products=updated, message=f"Updated {len(updated)} products", success=True)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

# Step 4: Custom Resolvers for Filtering & Sorting (Task 3)
def resolve_all_customers(root, info, **kwargs):
    # Default queryset
    queryset = Customer.objects.all()
    filterset = CustomerFilter(kwargs, queryset=queryset)
    queryset = filterset.qs
    # Sorting challenge
    order_by = kwargs.get('orderBy')  # Note: camelCase in GraphQL
    if order_by:
        queryset = queryset.order_by(order_by if not order_by.startswith('-') else order_by)
    return queryset

def resolve_all_products(root, info, **kwargs):
    queryset = Product.objects.all()
    filterset = ProductFilter(kwargs, queryset=queryset)
    queryset = filterset.qs
    order_by = kwargs.get('orderBy')
    if order_by:
        queryset = queryset.order_by(order_by if not order_by.startswith('-') else order_by)
    return queryset

def resolve_all_orders(root, info, **kwargs):
    queryset = Order.objects.all()
    filterset = OrderFilter(kwargs, queryset=queryset)
    queryset = filterset.qs
    order_by = kwargs.get('orderBy')
    if order_by:
        queryset = queryset.order_by(order_by if not order_by.startswith('-') else order_by)
    return queryset

# Step 5: Query Class LAST (now Types are defined)
class Query(graphene.ObjectType):
    hello = String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    # Filtered queries with sorting arg
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter,
        order_by=String(description="Order by (e.g., 'name' or '-name')")
    )
    all_customers.resolver = resolve_all_customers  # Bind custom resolver

    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter,
        order_by=String()
    )
    all_products.resolver = resolve_all_products

    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter,
        order_by=String()
    )
    all_orders.resolver = resolve_all_orders