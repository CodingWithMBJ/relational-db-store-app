from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


engine = create_engine("sqlite:///shop.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    orders = relationship("Order", backref="user")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)  # cents (188 = $1.88)

    orders = relationship("Order", backref="product")


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    shipped = Column(Boolean, default=False, nullable=False)


Base.metadata.create_all(engine)


# ------------------------
# ON-DEMAND ACTIONS
# ------------------------
def update_product_price(product_id, new_price_cents):
    session.query(Product).filter(Product.id == product_id).update(
        {Product.price: new_price_cents}
    )
    session.commit()


def delete_user_by_id(user_id):
    session.query(Order).filter(Order.user_id == user_id).delete()
    session.query(User).filter(User.id == user_id).delete()
    session.commit()


# -------------------------------------------------
# ORIGINAL DATA CREATION STEPS (COMMENTED OUT)
# -------------------------------------------------
# # USERS
# user1 = User(name="Johnny Bravo", email="jbravo@email.com")
# user2 = User(name="James Bond", email="jamesb@email.com")

# # PRODUCTS (cents)
# product1 = Product(name="Orange Juice", price=188)
# product2 = Product(name="Apple Juice", price=177)
# product3 = Product(name="Grape Juice", price=200)

# # ORDERS
# order1 = Order(user=user1, product=product1, quantity=2)
# order2 = Order(user=user1, product=product2, quantity=5)
# order3 = Order(user=user2, product=product3, quantity=1)
# order4 = Order(user=user2, product=product1, quantity=3)

# session.add_all([
#     user1, user2,
#     product1, product2, product3,
#     order1, order2, order3, order4
# ])
# session.commit()


# ------------------------
# RETRIEVE ALL USERS
# ------------------------
print("\nUSERS")
print("-" * 50)
for u in session.query(User).order_by(User.id):
    print(f"ID: {u.id} | Name: {u.name} | Email: {u.email}")

# ------------------------
# RETRIEVE ALL PRODUCTS
# ------------------------
print("\nPRODUCTS")
print("-" * 50)
for p in session.query(Product).order_by(Product.id):
    print(f"ID: {p.id} | Name: {p.name} | Price: {p.price / 100:.2f}")

# ------------------------
# RETRIEVE ALL ORDERS (user name, product name, quantity)
# ------------------------
print("\nORDERS")
print("-" * 50)
orders = (
    session.query(Order)
    .join(User)
    .join(Product)
    .order_by(Order.id)
    .all()
)
for o in orders:
    print(f"OrderID: {o.id} | User: {o.user.name} | Product: {o.product.name} | Qty: {o.quantity}")


# ------------------------
# RUN THESE ONLY WHEN YOU WANT (uncomment)
# ------------------------

# update_product_price(product_id=1, new_price_cents=249)  # $2.49
# delete_user_by_id(user_id=2)


# ------------------------
# COUNT ORDERS PER USER
# ------------------------
print("\nTOTAL ORDERS PER USER")
print("-" * 50)
counts = (
    session.query(User.name, func.count(Order.id))
    .join(Order)
    .group_by(User.id)
    .order_by(User.id)
    .all()
)
for name, total in counts:
    print(f"{name}: {total} order(s)")
