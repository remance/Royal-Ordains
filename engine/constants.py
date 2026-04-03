"""Constant value related to battle"""
Default_Screen_Width = 3840
Default_Screen_Height = 2160
Base_Animation_Frame_Play_Time = 0.1
Base_Region_Army_Travel_Time = 20
Battle_Speech_Font_Size = 50
Default_Air_Pos = 800
Default_Float_Pos = 1300
Default_Ground_Pos = 2000
Character_Gravity = 500
Collision_Grid_X_Per_Scene = 4
Collision_Grid_Y_Per_Scene = 2
Custom_Default_Culture = "castle"
Grand_Default_Faction = "masendor"
Default_Showcase_Character = "leader_vraesier"
Default_Selected_Stage_Custom_Battle = "stage_custom1"
Default_Supply_limit_Custom_Battle = 1000
Default_Gold_limit_Custom_Battle = 5000
Default_Weather_Custom_Battle = 1
Default_Weather_Strength_Custom_Battle = 0

# THESE CONSTANTS SHOULD NOT BE CHANGED
Default_Showcase_Character_POS = (Default_Screen_Width * 0.6, Default_Screen_Height * 0.6)
Default_Showcase_Character_air_POS = (Default_Screen_Width * 0.6, Default_Screen_Height * 0.45)
Weak_To_Element = {"fire": "water", "water": "air", "earth": "fire", "air": "earth", "magic": None,
                   "stab": None, "slash": None, "crush": None}
Opposite_Team = {1: 2, 2: 1}
