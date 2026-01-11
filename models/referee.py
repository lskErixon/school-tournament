from models.imports import *

RefereeLevel = Literal['student', 'teacher', 'external']

@dataclass
class Referee:
    referee_id: Optional[int]
    full_name: str
    email: str
    level: RefereeLevel
    active: bool
