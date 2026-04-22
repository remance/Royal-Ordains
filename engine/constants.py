Base_Animation_Frame_Play_Time = 0.1
Base_Region_Army_Travel_Time = 20
Battle_Speech_Font_Size = 50
Default_Battle_Air_Pos = 800
Default_Battle_Float_Pos = 1300
Default_Battle_Ground_Pos = 2000
Character_Gravity = 500

"""number of collision grids per scene in battle, more grids can improve collision detection performance when 
battle involve huge number of characters"""
Collision_Grid_X_Per_Battle_Scene = 4
Collision_Grid_Y_Per_Battle_Scene = 2

"""change to these value that no exist in data can break the game"""
Custom_Default_Culture = "castle"
Default_Showcase_Character = "leader_tulia"
Default_Selected_Stage_Custom_Battle = "stage_custom1"

Default_Supply_limit_Custom_Battle = 1000
Default_Gold_limit_Custom_Battle = 5000
Default_Weather_Custom_Battle = 1
Default_Weather_Strength_Custom_Battle = 0
Retinue_Leadership_Add_Modifier = 0.3

Phase_To_Game_Time = 1  # in second to 1 phase
Turn_To_Phase = 11  # in phase to 1 turn
Phase_To_Battle_Time = 60  # in second

"""culture policy for grand campaign
ANY CHANGE IN KEYS WILL CAUSE ERRORS from the inconsistency in game code, uigrand and ui sprite asset
the value indicate maximum integration value that the culture can reach"""
Culture_Policy_Integration = {"reject": -1, "tolerate": 0.1, "restrict": 0.35, "partial": 0.65, "accept": 1}
Culture_Policy_Relation = {"reject": -30, "tolerate": 0, "restrict": -15, "partial": -5, "accept": 10}

"""Route type travel modifier for army in grand campaign"""
Route_Travel_Modifier = {"land": 1, "forest": 2, "hill": 2, "snow": 2, "sea": 3, "mountain": 3, "ocean": 4}

# DO NOT CHANGE BELOW AS THEY MAY BREAK THE GAME
Default_Screen_Width = 3840
Default_Screen_Height = 2160
Default_Showcase_Character_POS = (Default_Screen_Width * 0.6, Default_Screen_Height * 0.6)
Default_Showcase_Character_air_POS = (Default_Screen_Width * 0.6, Default_Screen_Height * 0.45)
Weak_To_Element = {"fire": "water", "water": "air", "earth": "fire", "air": "earth", "magic": None,
                   "stab": None, "slash": None, "crush": None}
Opposite_Team = {1: 2, 2: 1}
