from pydantic import BaseModel
from datetime import datetime
from typing import List
from enum import Enum
from models.payment import PaymentMethod

class SalesHistoryItem(BaseModel):
    order_id: int
    created_at: datetime
    total: float
    method: PaymentMethod
    dish_names: List[str]

class PaginatedSalesHistory(BaseModel):
    items: List[SalesHistoryItem]
    total_pages: int
    current_page: int
    total_items: int

class TopDish(BaseModel):
    name: str
    quantity: int

class PopularFloor(BaseModel):
    name: str
    orders: int
    revenue: float

class SalesPerDay(BaseModel):
    date: str
    revenue: float

class SalesPerWeek(BaseModel):
    week: str
    revenue: float

class SalesPerMonth(BaseModel):
    month: str
    revenue: float

class ProjectionTimeframe(str, Enum):
    NEXT_WEEK_DAILY = "NEXT_WEEK_DAILY"
    NEXT_MONTH_DAILY = "NEXT_MONTH_DAILY"
    TOMORROW_HOURLY = "TOMORROW_HOURLY"

class Projection(BaseModel):
    date: str
    expected_revenue: float

class ProjectionResponse(BaseModel):
    success: bool
    message: str
    projections: List[Projection]

class DiscountRecommendation(BaseModel):
    dish_id: int
    dish_name: str
    current_price: float
    current_cost: float
    margin_percentage: float
    predicted_sales_next_week: int
    reason: str

class DashboardStats(BaseModel):
    total_revenue: float
    total_orders: int
    top_dishes: List[TopDish]
    popular_floors: List[PopularFloor]
    sales_per_day: List[SalesPerDay]
    sales_per_week: List[SalesPerWeek]
    sales_per_month: List[SalesPerMonth]
    discount_recommendations: List[DiscountRecommendation] = []
