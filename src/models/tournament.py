from src.models.imports import *

@dataclass
class Tournament:
    tournament_id: Optional[int]
    name: str
    start_date: date
    end_date: Optional[date]
    is_active: bool
