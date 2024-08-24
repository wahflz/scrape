from dataclasses import dataclass

@dataclass
class JobPosition:
    name: str
    shifts: int
    code: str

@dataclass
class JobLocation:
    city: str
    state: str
    distance: float

@dataclass
class JobItem:
    position: JobPosition
    location: JobLocation
