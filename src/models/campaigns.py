from dataclasses import dataclass, asdict

@dataclass
class Campaign:
    campaign_id: str
    name: str
    target_audience: str
    start_time: str
    schedule: str
    duration: int
    questions: list
    type: str
    status: str

    def to_dict(self):
        return asdict(self)
