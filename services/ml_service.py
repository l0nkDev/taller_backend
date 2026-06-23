import pandas as pd
from sqlmodel import Session, select
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

from models.payment import Payment
from models.order import Order
from models.order_detail import OrderDetail
from models.dish import Dish
from schemas.bi_schemas import (
    Projection,
    ProjectionResponse,
    ProjectionTimeframe,
    DiscountRecommendation,
)


def generate_projections(
    session: Session,
    timeframe: ProjectionTimeframe = ProjectionTimeframe.NEXT_WEEK_DAILY,
) -> ProjectionResponse:
    # 1. Fetch all historical payments
    payments = session.exec(
        select(Payment).join(Order).where(Order.was_paid == True)
    ).all()

    if len(payments) < 10:
        return ProjectionResponse(
            success=False,
            message="Se requiere más historial de ventas para generar proyecciones.",
            projections=[],
        )

    # 2. Prepare Data
    data = []
    for p in payments:
        data.append(
            {
                "datetime": p.created_at,
                "date": p.created_at.date(),
                "hour": p.created_at.hour,
                "revenue": p.total,
            }
        )

    df = pd.DataFrame(data)

    if timeframe == ProjectionTimeframe.TOMORROW_HOURLY:
        # Aggregate by date and hour
        hourly_revenue = (
            df.groupby(["date", "hour"])["revenue"].sum().reset_index()
        )
        hourly_revenue = hourly_revenue.sort_values(["date", "hour"])

        if len(hourly_revenue) < 24:
            return ProjectionResponse(
                success=False,
                message="No hay suficiente historial por hora.",
                projections=[],
            )

        hourly_revenue["date"] = pd.to_datetime(hourly_revenue["date"])
        hourly_revenue["day_of_week"] = hourly_revenue["date"].dt.dayofweek
        hourly_revenue["is_weekend"] = hourly_revenue["day_of_week"].apply(
            lambda x: 1 if x >= 5 else 0
        )

        # Lag feature (previous hour revenue)
        hourly_revenue["prev_hour_revenue"] = hourly_revenue["revenue"].shift(
            1
        )
        ml_df = hourly_revenue.dropna()

        X = ml_df[["day_of_week", "is_weekend", "hour", "prev_hour_revenue"]]
        y = ml_df["revenue"]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        last_date = hourly_revenue["date"].iloc[-1]
        hourly_revenue["hour"].iloc[-1]
        last_revenue = hourly_revenue["revenue"].iloc[-1]

        # Predict for tomorrow from 08:00 to 23:00
        tomorrow = datetime.now().date() + timedelta(days=1)

        projections = []
        current_prev_revenue = last_revenue

        for h in range(8, 24):
            next_features = pd.DataFrame(
                {
                    "day_of_week": [tomorrow.weekday()],
                    "is_weekend": [1 if tomorrow.weekday() >= 5 else 0],
                    "hour": [h],
                    "prev_hour_revenue": [current_prev_revenue],
                }
            )

            pred_revenue = model.predict(next_features)[0]
            pred_revenue = max(0, pred_revenue)

            projections.append(
                Projection(
                    date=f"{tomorrow.strftime('%Y-%m-%d')} {str(h).zfill(2)}:00",
                    expected_revenue=round(pred_revenue, 2),
                )
            )
            current_prev_revenue = pred_revenue

        return ProjectionResponse(
            success=True,
            message="Proyecciones por hora generadas.",
            projections=projections,
        )

    else:
        # Daily aggregations for NEXT_WEEK_DAILY and NEXT_MONTH_DAILY
        daily_revenue = df.groupby("date")["revenue"].sum().reset_index()
        daily_revenue = daily_revenue.sort_values("date")

        # If we have less than 7 days of aggregated data, abort
        if len(daily_revenue) < 7:
            return ProjectionResponse(
                success=False,
                message="Se requieren al menos 7 días de historial para generar proyecciones.",
                projections=[],
            )

        # 3. Feature Engineering
        daily_revenue["date"] = pd.to_datetime(daily_revenue["date"])
        daily_revenue["day_of_week"] = daily_revenue["date"].dt.dayofweek
        daily_revenue["is_weekend"] = daily_revenue["day_of_week"].apply(
            lambda x: 1 if x >= 5 else 0
        )
        daily_revenue["month"] = daily_revenue["date"].dt.month

        # Lag features (previous day revenue)
        daily_revenue["prev_day_revenue"] = daily_revenue["revenue"].shift(1)

        # Drop rows with NaN (due to shift)
        ml_df = daily_revenue.dropna()

        # 4. Train Model
        X = ml_df[["day_of_week", "is_weekend", "month", "prev_day_revenue"]]
        y = ml_df["revenue"]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # 5. Predict
        last_date = daily_revenue["date"].iloc[-1]
        last_revenue = daily_revenue["revenue"].iloc[-1]

        days_to_predict = (
            7 if timeframe == ProjectionTimeframe.NEXT_WEEK_DAILY else 30
        )

        projections = []
        current_prev_revenue = last_revenue

        for i in range(1, days_to_predict + 1):
            next_date = last_date + pd.Timedelta(days=i)

            # Prepare features for prediction
            next_features = pd.DataFrame(
                {
                    "day_of_week": [next_date.dayofweek],
                    "is_weekend": [1 if next_date.dayofweek >= 5 else 0],
                    "month": [next_date.month],
                    "prev_day_revenue": [current_prev_revenue],
                }
            )

            pred_revenue = model.predict(next_features)[0]

            # Prevent negative predictions
            pred_revenue = max(0, pred_revenue)

            projections.append(
                Projection(
                    date=next_date.strftime("%Y-%m-%d"),
                    expected_revenue=round(pred_revenue, 2),
                )
            )

            current_prev_revenue = pred_revenue

        return ProjectionResponse(
            success=True,
            message=f"Proyecciones generadas para {days_to_predict} días.",
            projections=projections,
        )


def generate_discount_recommendations(
    session: Session,
) -> list[DiscountRecommendation]:
    # Fetch orders and details
    details_query = (
        select(OrderDetail).join(Order).where(Order.was_paid == True)
    )
    details = session.exec(details_query).all()

    if not details:
        return []

    data = []
    for d in details:
        if d.dish_id:
            data.append(
                {
                    "dish_id": d.dish_id,
                    "date": d.order.created_at.date(),
                    "quantity": d.quantity,
                }
            )

    if not data:
        return []

    df = pd.DataFrame(data)

    recommendations = []
    dishes = session.exec(select(Dish).where(Dish.available == True)).all()

    for dish in dishes:
        if dish.price is None or dish.price <= 0:
            continue

        cost = dish.cost or 0.0
        margin = (dish.price - cost) / dish.price

        # Only analyze if margin > 50%
        if margin <= 0.50:
            continue

        # Filter df for this dish
        dish_df = df[df["dish_id"] == dish.id]

        if len(dish_df) == 0:
            continue

        # Group by date
        daily_qty = dish_df.groupby("date")["quantity"].sum().reset_index()
        daily_qty["date"] = pd.to_datetime(daily_qty["date"])

        # We need at least 3 days of sales for a tiny bit of history to avoid crashing
        if len(daily_qty) < 3:
            continue

        daily_qty = daily_qty.sort_values("date")
        daily_qty["day_of_week"] = daily_qty["date"].dt.dayofweek
        daily_qty["prev_day_qty"] = daily_qty["quantity"].shift(1)

        ml_df = daily_qty.dropna()
        if len(ml_df) == 0:
            continue

        X = ml_df[["day_of_week", "prev_day_qty"]]
        y = ml_df["quantity"]

        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X, y)

        last_date = daily_qty["date"].iloc[-1]
        last_qty = daily_qty["quantity"].iloc[-1]

        predicted_total = 0
        current_prev = last_qty

        for i in range(1, 8):  # Next 7 days
            next_date = last_date + pd.Timedelta(days=i)
            next_features = pd.DataFrame(
                {
                    "day_of_week": [next_date.dayofweek],
                    "prev_day_qty": [current_prev],
                }
            )

            pred = model.predict(next_features)[0]
            pred = max(0, pred)
            predicted_total += pred
            current_prev = pred

        predicted_sales = int(round(predicted_total))

        # If predicted next week sales is < 15, recommend discount!
        if predicted_sales < 15:
            reason = f"Tiene un alto margen de ganancia ({int(margin * 100)}%), pero el modelo proyecta bajas ventas ({predicted_sales} unidades) para la próxima semana. Un descuento podría impulsar la demanda sin comprometer utilidades."
            recommendations.append(
                DiscountRecommendation(
                    dish_id=dish.id,
                    dish_name=dish.name,
                    current_price=dish.price,
                    current_cost=cost,
                    margin_percentage=margin,
                    predicted_sales_next_week=predicted_sales,
                    reason=reason,
                )
            )

    return recommendations
