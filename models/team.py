from imports import *

@dataclass
class Team:
    team_id: Optional[int]
    name: str
    class_name: str
    rating: float
    is_deleted: bool
