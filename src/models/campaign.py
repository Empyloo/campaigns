# Path: src/models/campaign.py
import datetime as dt
from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class Campaign:
    name: str
    count: int
    threshold: int
    status: str
    company_id: str
    created_by: str
    next_run_time: dt.datetime
    type: Optional[str] = None
    duration: Optional[str] = None
    end_date: Optional[dt.datetime] = None
    frequency: Optional[str] = None
    time_of_day: Optional[dt.time] = None
    description: Optional[str] = None
    audience_ids: Optional[List[str]] = None
    questionnaire_ids: Optional[List[str]] = None
    cloud_task_id: Optional[str] = None

    def to_rpc_params(self):
        """Converts the fields into a dictionary with keys prefixed with an underscore."""
        return {f"_{k}": v for k, v in asdict(self).items()}
