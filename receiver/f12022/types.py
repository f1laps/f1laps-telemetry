SessionType = {
     0: "unknown",
     1: "practice_1",
     2: "practice_2",
     3: "practice_3",
     4: "practice_short",
     5: "qualifying_1",
     6: "qualifying_2",
     7: "qualifying_3",
     8: "qualifying", # short
     9: "qualifying", # OSQ
    10: "race",
    11: "race",
    12: "race",
    13: "time_trial",
}

# Race and OSQ have outlaps
SESSION_TYPES_WITH_OUTLAP = [10, 11, 12, 9]
# Quali non-one-shot have in- and outlaps
SESSION_TYPES_WITH_IN_AND_OUT_LAP = [5, 6, 7, 8]
# Time trial IDs (needed because they have their own lap rules)
SESSION_TYPES_TIME_TRIAL = [13]


Track = {
     0: "Melbourne",
     1: "Paul Ricard",
     2: "Shanghai",
     3: "Sakhir (Bahrain)",
     4: "Catalunya",
     5: "Monaco",
     6: "Montreal",
     7: "Silverstone",
     8: "Hockenheim",
     9: "Hungaroring",
    10: "Spa",
    11: "Monza",
    12: "Singapore",
    13: "Suzuka",
    14: "Abu Dhabi",
    15: "Texas",
    16: "Brazil",
    17: "Austria",
    18: "Sochi",
    19: "Mexico",
    20: "Baku (Azerbaijan)",
    21: "Sakhir Short",
    22: "Silverstone Short",
    23: "Texas Short",
    24: "Suzuka Short",
    25: "Hanoi",
    26: "Zandvoort",
    27: "Imola",
    28: "Portimão",
    29: "Jeddah",
}