from models.imports import *

PlayerPosition = Literal['GK', 'DEF', 'MID', 'ATT']

@dataclass
class Player:
    player_id: Optional[int]
    team_id: int
    first_name: str
    last_name: str
    birth_date: date
    position: PlayerPosition
