from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from datetime import datetime
from typing import List

from database import get_session
from core.security import get_current_active_user
from models.user import User
from schemas.bi_schemas import SalesHistoryItem, DashboardStats, ProjectionResponse, PaginatedSalesHistory, ProjectionTimeframe
from services import bi_service, ml_service

router = APIRouter(prefix="/bi", tags=["bi"])

@router.get("/sales-history", response_model=PaginatedSalesHistory)
def get_sales_history(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    dish_name: str = Query(None),
    category_id: int = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return bi_service.get_sales_history(session, start_date, end_date, dish_name, category_id, page, page_size)

@router.get("/dashboard-stats", response_model=DashboardStats)
def get_dashboard_stats(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return bi_service.get_dashboard_stats(session, start_date, end_date)

@router.get("/projections", response_model=ProjectionResponse)
def get_projections(
    timeframe: ProjectionTimeframe = Query(ProjectionTimeframe.NEXT_WEEK_DAILY),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return ml_service.generate_projections(session, timeframe)
