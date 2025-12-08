# moveset calculation
stat_multiplier = 1.0
pp_multiplier = 0.5
multiple_same_type_multiplier = 0.75


# type_damage_matrix
type_matrix = {
    "normal":   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0, 1, 1, 0.5, 1],
    "grass":    [1, 0.5, 0.5, 2, 1, 1, 1, 0.5, 2, 0.5, 1, 0.5, 2, 1, 0.5, 1, 0.5, 1],
    "fire":     [1, 2, 0.5, 0.5, 1, 2, 1, 1, 1, 1, 1, 2, 0.5, 1, 0.5, 1, 2, 1],
    "water":    [1, 0.5, 2, 0.5, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 0.5, 1, 1, 1],
    "electric": [1, 0.5, 1, 2, 0.5, 1, 1, 1, 0, 2, 1, 1, 1, 1, 0.5, 1, 1, 1],
    "ice":      [1, 2, 0.5, 0.5, 1, 0.5, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 0.5, 1],
    "fighting": [2, 1, 1, 1, 1, 2, 1, 0.5, 1, 0.5, 0.5, 0.5, 2, 0, 1, 2, 2, 0.5],
    "poison":   [1, 2, 1, 1, 1, 1, 1, 0.5, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, 0, 2],
    "ground":   [1, 0.5, 2, 1, 2, 1, 1, 2, 1, 0, 1, 0.5, 2, 1, 1, 1, 2, 1],
    "flying":   [1, 2, 1, 1, 0.5, 1, 2, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 0.5, 1],
    "psychic":  [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0.5, 1, 1, 1, 1, 0, 0.5, 1],
    "bug":      [1, 2, 0.5, 1, 1, 1, 0.5, 0.5, 1, 0.5, 2, 1, 1, 0.5, 1, 2, 0.5, 0.5],
    "rock":     [1, 1, 2, 1, 1, 2, 0.5, 1, 0.5, 2, 1, 2, 1, 1, 1, 1, 0.5, 1],
    "ghost":    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 1],
    "dragon":   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0.5, 0],
    "dark":     [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 0.5],
    "steel":    [1, 1, 0.5, 0.5, 0.5, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0.5, 2],
    "fairy":    [1, 1, 0.5, 1, 1, 1, 2, 0.5, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 1],
}

type_ids = {
    -1: "UNKNOWN",
    0: "NORMAL",
    1: "FIGHTING",
    2: "FLYING",
    3: "POISON",
    4: "GROUND",
    5: "ROCK",
    6: "BUG",
    7: "GHOST",
    8: "STEEL",
    9: "FIRE",
    10: "WATER",
    11: "GRASS",
    12: "ELECTRIC",
    13: "PSYCHIC",
    14: "ICE",
    15: "DRAGON",
    16: "DARK",
    17: "FAIRY",
    18: "STELLAR"
}

form_ids = {
    0: "",  # normal form
    1: "mega",
    2: "mega-x",
    3: "mega-y",
    4: "primal",
    5: "origin",
    6: "incarnate",
    7: "therian",
    8: "gigantamax",
    9: "gigantamax-single",
    10: "gigantamax-rapid",
    11: "eternamax",
}

status_matrix = {
    "none": float(),
    "paralyzed": float(),
    "poisoned": float(),
    "burned": float(),
    "frozen": float(),
    "asleep": float(),
}


screen = (1920, 1080)
roi_stage = (1100, -55, 1820, 0)
roi_game = (96, 52, 1823, 1023)
roi_main_menu = (1460, 563, 1778, 978)
image_scaler = (1/3, 1/3)
scaled_game_width = int((roi_game[2] - roi_game[0]) * image_scaler[0])
scaled_game_height = int((roi_game[3] - roi_game[1]) * image_scaler[1])

scaled_screen_width = int(screen[0] * image_scaler[0])
scaled_screen_height = int(screen[1] * image_scaler[1])
action_keymap = {
    0: 'w',  # Up
    1: 'a',  # Left
    2: 's',  # Down
    3: 'd',  # Right
    4: 'Space',  # Confirm / Action
    5: 'Backspace',  # Back / Cancel
    6: 'Enter'  # Start
}

BUTTON_KEYCODES = {
    "UP": 38,
    "DOWN": 40,
    "LEFT": 37,
    "RIGHT": 39,
    "ENTER": 13,
    "SPACE": 32,
    "BACKSPACE": 8,
    "C": 67,
}

phases = {
    "nothing_to_do": ["EncounterPhase", "SummonPhase", "LoginPhase", "InitEncounterPhase", "PostSummonPhase", "TurnInitPhase", "EnemyCommandPhase",
                      "VictoryPhase", "ShowPartyExpBarPhase", "HidePartyExpBarPhase", "LevelUpPhase", "MoveEndPhase", "MovePhase",
                      "CheckInterludePhase", "WeatherEffectPhase", "PositionalTagPhase", "BerryPhase", "CheckStatusEffectPhase", "TurnEndPhase",
                      "BattleEndPhase", "EggLapsePhase", "NewBattlePhase", "NextEncounterPhase", "ToggleDoublePositionPhase", "TurnStartPhase",
                      "MoveEffectPhase", "DamageAnimPhase", "FaintPhase", "StatStageChangePhase", "ShowTrainerPhase", "MessagePhase",
                      "SwitchSummonPhase", "HideAbilityPhase", "ShowAbilityPhase", "ReturnPhase", "TeraPhase", "PostGameOverPhase", "AttemptRunPhase",
                      "SelectBiomePhase", "PartyHealPhase", "ResetStatusPhase", "SwitchBiomePhase", "NewBiomeEncounterPhase", "ShinySparklePhase"],  # you can't really do anything here
    "skip_information": ["MessagePhase", "ExpPhase", "MoneyRewardPhase", "LevelCapPhase"],  # you can only press space to accept, no options
    "complicated": ["CheckSwitchPhase", "TitlePhase", "CommandPhase", "LearnMovePhase", "SelectModifierPhase", "AttemptCapturePhase",
                    "NextEncounterPhase", "SwitchPhase", "TrainerVictoryPhase", "GameOverPhase", "SelectStarterPhase", "SelectTargetPhase",
                    "EggLapsePhase", "EggSummaryPhase", "ModifierRewardPhase", "SelectBiomePhase", "EggHatchPhase", "ScanIvsPhase"],  # phases with more than one option
}


phasesinfo ="""
 -Check SwitchPhase = nicht switchen
 -Title Phase = main menu aber für terminated Check und random pokemon wählen / Start runnen aka Tastenkombi für neuen Run
 -CommandPhase = Battle Single vs Double checken + Move wählen
 -LearnMovePhase = 1-5 Random ausgeben wobei 5 für "verlernen" steht = ca 5 mal Space oder so
 -SelectModifierPhase = "Maybe der Shop" = Random 1-3 auswählen 
> Items müssen trotzdem etwas modelliert werden weil items manchmal angewenedet werden müssen

-Attempt Capture Phase = Nur wenn wir fangen wollen würden
-Next Encounter Phase = wahrscheinlich skippen oder wird geskippt ( Timer + Space)
-SwitchPhase = (2 Müssen extra handeln wegen doppelkopf - Smart Liste ausgeben lassen, welches am leben und random auswählen)
-Trainer Victory Phase = EGAL
-GameOverPhase = EGAL weil Settings aus
-SelectStarterPhase = EGAL weil hardcoded
-Select Target Phase = ???
-EggLapsePhase = Skip
-EggSummaryPhase = BACKSPACE
-Modifier Reward Phase = Wahrscheinlich SKIP
-SelectBiomePhase = Only with MAP (Do not take map or only first biome always)
-EggHatchPhase = ???
-ScanIvsPhase = EGAL weil Settings
"""

biomes = ["Abyss", "Ancient Ruins", "Badlands", "Beach", "Cave", "Construction Site", "Desert", "Dojo", "Factory", "Fairy Cave", "Forest",
          "Grassy Fields", "Graveyard", "Ice Cave", "Island", "Jungle", "Laboratory", "Lake", "Meadow", "Metropolis", "Mountain", "Plains",
          "Power Plant", "Sea", "Seabed", "Slum", "Snowy Forest", "Space", "Swamp", "Tall Grass", "Temple", "Town", "Volcano", "Wasteland", "End"]

reward_weights = {
    # hp delta
    "damage_dealt": 1.0,
    "damage_taken": 1.25,
    "hp": 100,  # delta is percentage
    "member_died": -50,
    # stages
    "wave_done": 10,
    "tenth_wave_done": 20,
}

item_weights = {
    "id": {
        "BASE_STAT_BOOSTER": 0,
        "EXP_SHARE": 5,
        "AMULET_COIN": 5,
        "WIDE_LENS": 0,
        "SUPER_EXP_CHARM": 5,
        "EXP_CHARM": 5,
        "BERRY": 0,
        "GRIP_CLAW": 0,
        "CANDY_JAR": 4,
        "GOLDEN_POKEBALL": 6,
        "ABILITY_CHARM": 5,
        "MEGA_BRACELET": 4,
        "ATTACK_TYPE_BOOSTER": 0,
        "CATCHING_CHARM": 4,
        "QUICK_CLAW": 0,
        "SOOTHE_BELL": 0,
        "RARE_FORM_CHANGE_ITEM": 0,
        "DYNAMAX_BAND": 4,
        "HEALING_CHARM": 5,
        "LUCKY_EGG": 0,
        "LEFTOVERS": 0,
        "LOCK_CAPSULE": 4,
        "SHELL_BELL": 0,
        "FOCUS_BAND": 0,
        "SOUL_DEW": 0,
        "BERRY_POUCH": 6,
        "IV_SCANNER": 4,
        "REVIVER_SEED": 0,
        "SCOPE_LENS": 0,
        "MULTI_LENS": 0,
        "KINGS_ROCK": 0,
        "SHINY_CHARM": 4,
        # until 100
        },
    "tier": {}
}
