from receiver.penalty_base import PenaltyBase
from receiver.f12022.api import F1LapsAPI2022

class F12022Penalty(PenaltyBase):
    f1laps_api_class = F1LapsAPI2022
