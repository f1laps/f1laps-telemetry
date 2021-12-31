from receiver.penalty_base import PenaltyBase
from receiver.f12021.api import F1LapsAPI2021

class F12021Penalty(PenaltyBase):
    f1laps_api_class = F1LapsAPI2021
