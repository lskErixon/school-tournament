from models.imports import *

MatchEventType = Literal['goal', 'own_goal', 'yellow', 'red']

@dataclass
class MatchEvent:
    event_id: Optional[int]
    match_id: int
    player_id: Optional[int]
    team_id: int
    minute: int
    event_type: MatchEventType
    xg: Optional[float]
    created_at: datetime
