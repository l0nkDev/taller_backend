import sys
import os
import random
from datetime import datetime, timedelta

# Add parent dir to path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlmodel import Session, select
from models.category import Category
from models.dish import Dish
from models.dish_price import DishPrice
from models.user import User
from models.table_group import TableGroup
from models.order import Order
from models.order_detail import OrderDetail, DetailStatus
from models.payment import Payment, PaymentMethod
from models.table import Table
from models.floor import Floor
from models.wall import Wall

def seed_data():
    with Session(engine) as session:
        # Check existing basics
        users = session.exec(select(User)).all()
        if not users:
            print("No users found. Please create some users first via the app.")
            return
        waiter = users[0]
        
        table_groups = session.exec(select(TableGroup)).all()
        if not table_groups:
            print("No table groups found. Please create a floorplan first.")
            return
            
        dishes = session.exec(select(Dish)).all()
        dish_prices = session.exec(select(DishPrice)).all()
        if not dishes or not dish_prices:
            print("No dishes or prices found. Please create a menu first.")
            return

        print("Starting seeding process... this may take a minute.")
        
        # We will seed 90 days (3 months)
        start_date = datetime.now() - timedelta(days=90)
        
        for day_offset in range(90):
            current_date = start_date + timedelta(days=day_offset)
            is_weekend = current_date.weekday() >= 5
            
            # Base number of orders: 15-25 on weekdays, 35-50 on weekends to guarantee 2000+ total
            num_orders = random.randint(35, 50) if is_weekend else random.randint(15, 25)
            
            # Seasonal trend: sales increase over the 90 days by ~20%
            trend_multiplier = 1.0 + (day_offset / 90.0) * 0.2
            num_orders = int(num_orders * trend_multiplier)
            
            for _ in range(num_orders):
                # Randomize time within the day (e.g., 11:00 to 22:00)
                hour = random.randint(11, 21)
                minute = random.randint(0, 59)
                order_time = current_date.replace(hour=hour, minute=minute)
                
                order = Order(
                    tablegroup_id=random.choice(table_groups).id,
                    created_at=order_time,
                    was_paid=True
                )
                
                num_details = random.randint(1, 5)
                total_amount = 0.0
                order_details = []
                for _ in range(num_details):
                    dish_price = random.choice(dish_prices)
                    quantity = random.randint(1, 3)
                    total_amount += dish_price.price * quantity
                    
                    detail = OrderDetail(
                        price_id=dish_price.id,
                        dish_name=dish_price.dish.name,
                        quantity=quantity,
                        discount=0.0,
                        status=DetailStatus.SERVED
                    )
                    order_details.append(detail)
                
                order.detail = order_details
                
                payment = Payment(
                    method=random.choice([PaymentMethod.CASH, PaymentMethod.QR]),
                    total=total_amount,
                    created_at=order_time + timedelta(minutes=random.randint(45, 90))
                )
                
                order.payment = payment
                session.add(order)
                
        session.commit()
        print("Seeding complete! Added 3 months of historical data with high volume.")

if __name__ == "__main__":
    seed_data()
