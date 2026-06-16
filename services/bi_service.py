from sqlmodel import Session, select
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from models.payment import Payment
from models.order import Order
from models.order_detail import OrderDetail, DetailStatus
from models.dish_price import DishPrice
from models.dish import Dish
from models.table_group import TableGroup
from collections import defaultdict
import math
from schemas.bi_schemas import SalesHistoryItem, PaginatedSalesHistory, DashboardStats, TopDish, PopularFloor, SalesPerDay, SalesPerWeek, SalesPerMonth

def get_sales_history(
    session: Session, 
    start_date: datetime | None = None, 
    end_date: datetime | None = None,
    dish_name: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    page_size: int = 20
) -> PaginatedSalesHistory:
    query = select(Payment).join(Order).where(Order.was_paid == True)
    
    if start_date:
        query = query.where(Payment.created_at >= start_date)
    if end_date:
        query = query.where(Payment.created_at <= end_date)
        
    if dish_name or category_id is not None:
        query = query.join(Order.detail).join(OrderDetail.price).join(DishPrice.dish)
        if dish_name:
            query = query.where(Dish.name.ilike(f"%{dish_name}%"))
        if category_id is not None:
            query = query.where(Dish.category_id == category_id)
            
    # Subquery count
    count_query = select(func.count()).select_from(query.subquery())
    total_items = session.exec(count_query).one()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    offset = (page - 1) * page_size
    query = query.order_by(Payment.created_at.desc()).offset(offset).limit(page_size)
    query = query.options(
        selectinload(Payment.order).selectinload(Order.detail)
    )
    
    payments = session.exec(query).all()
    
    results = []
    for payment in payments:
        order = payment.order
        dish_names = []
        for detail in order.detail:
            if detail.status != DetailStatus.CANCELLED and detail.dish_name:
                dish_names.append(f"{detail.quantity}x {detail.dish_name}")
        
        results.append(SalesHistoryItem(
            order_id=payment.order_id,
            created_at=payment.created_at,
            total=payment.total,
            method=payment.method,
            dish_names=dish_names
        ))
        
    return PaginatedSalesHistory(
        items=results,
        total_pages=total_pages,
        current_page=page,
        total_items=total_items
    )

def get_dashboard_stats(session: Session, start_date: datetime | None = None, end_date: datetime | None = None) -> DashboardStats:
    # Query total revenue and total orders
    payment_query = select(Payment).join(Order).where(Order.was_paid == True).options(
        selectinload(Payment.order).selectinload(Order.tablegroup).selectinload(TableGroup.floor)
    )
    if start_date:
        payment_query = payment_query.where(Payment.created_at >= start_date)
    if end_date:
        payment_query = payment_query.where(Payment.created_at <= end_date)
        
    payments = session.exec(payment_query).all()
    total_revenue = sum(p.total for p in payments)
    total_orders = len(payments)
    
    # Query top selling dishes
    detail_query = select(
        Dish.name,
        func.sum(OrderDetail.quantity).label("total_quantity")
    ).join(
        DishPrice, OrderDetail.price_id == DishPrice.id
    ).join(
        Dish, DishPrice.dish_id == Dish.id
    ).join(
        Order, OrderDetail.order_id == Order.id
    ).where(
        Order.was_paid == True,
        OrderDetail.status != DetailStatus.CANCELLED
    )
    
    if start_date:
        detail_query = detail_query.where(Order.created_at >= start_date)
    if end_date:
        detail_query = detail_query.where(Order.created_at <= end_date)
        
    detail_query = detail_query.group_by(Dish.name).order_by(func.sum(OrderDetail.quantity).desc()).limit(10)
    
    top_dishes_raw = session.exec(detail_query).all()
    top_dishes = [TopDish(name=row[0], quantity=row[1]) for row in top_dishes_raw]
    
    floor_stats = defaultdict(lambda: {"orders": 0, "revenue": 0.0})
    daily_stats = defaultdict(float)
    weekly_stats = defaultdict(float)
    monthly_stats = defaultdict(float)

    for p in payments:
        day_str = p.created_at.strftime('%Y-%m-%d')
        daily_stats[day_str] += p.total
        
        week_str = p.created_at.strftime('%Y-W%W')
        weekly_stats[week_str] += p.total
        
        month_str = p.created_at.strftime('%Y-%m')
        monthly_stats[month_str] += p.total
        
        if p.order and p.order.tablegroup and p.order.tablegroup.floor:
            floor_name = p.order.tablegroup.floor.name
            floor_stats[floor_name]["orders"] += 1
            floor_stats[floor_name]["revenue"] += p.total

    popular_floors = [
        PopularFloor(name=k, orders=v["orders"], revenue=v["revenue"])
        for k, v in sorted(floor_stats.items(), key=lambda item: item[1]["revenue"], reverse=True)
    ]
    
    sales_per_day = [
        SalesPerDay(date=k, revenue=v)
        for k, v in sorted(daily_stats.items())
    ]
    
    sales_per_week = [
        SalesPerWeek(week=k, revenue=v)
        for k, v in sorted(weekly_stats.items())
    ]
    
    sales_per_month = [
        SalesPerMonth(month=k, revenue=v)
        for k, v in sorted(monthly_stats.items())
    ]
    
    return DashboardStats(
        total_revenue=total_revenue,
        total_orders=total_orders,
        top_dishes=top_dishes,
        popular_floors=popular_floors,
        sales_per_day=sales_per_day,
        sales_per_week=sales_per_week,
        sales_per_month=sales_per_month
    )
