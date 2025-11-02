from enum import Enum
class State(Enum):
    """Attribute different states of the game within those Enums"""
    NOT_STARTED=0
    PLAYING=1
    PLAY_ITEM=2
    CANT_PLAY_ITEM=3 
    RECLICK=4
    O_WIN=5
    X_WIN=6
    GAME_DRAW=7
    """States used specifically to know where the user clicked"""
    BOARD=11
    RECLICKING=12
    DRAWING=13
    OVERLAY_ITEM=14
    INVENTORY=15
    NOT_DEFINED=16