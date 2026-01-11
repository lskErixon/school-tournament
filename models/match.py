from models.imports import *

MatchStatus = Literal['scheduled', 'live', 'finished', 'cancelled']

@dataclass
class Match:
    match_id: Optional[int]
    tournament_id: int
    home_team_id: int
    away_team_id: int
    start_time: datetime
    status: MatchStatus
    is_overtime: bool
