from datetime import date

from pydantic import BaseModel


class WeeklyTrainingAgg(BaseModel):
    user_id: str
    week_start: date
    total_distance_m: float
    avg_heart_rate: float
