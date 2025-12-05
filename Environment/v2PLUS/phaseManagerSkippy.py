# Script for correctly skipping phases in v2PLUS environment based on hardcoded logic

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

phases_skip_logic = {
    "CheckSwitchPhase": {"action": "no_switch"},
    "TitlePhase": {"action": "start_run"},
    "CommandPhase": {"action": "choose_move"},
    "LearnMovePhase": {"action": "learn_move_random", "choices": [1, 2, 3, 4, 5]},
    "SelectModifierPhase": {"action": "select_modifier_random", "min": 1, "max": 3}, #TODO
    "AttemptCapturePhase": {"action": "attempt_capture_conditional"}, # Not needed
    "NextEncounterPhase": {"action": "skip"},
    "SwitchPhase": {"action": "smart_switch"},
    "TrainerVictoryPhase": {"action": "ignore"},
    "GameOverPhase": {"action": "ignore"},
    "SelectStarterPhase": {"action": "ignore"},
    "SelectTargetPhase": {"action": "select_target_best_effort"},
    "EggLapsePhase": {"action": "skip"},
    "EggSummaryPhase": {"action": "backspace"},
    "ModifierRewardPhase": {"action": "skip"},
    "SelectBiomePhase": {"action": "select_biome_first_only"},
    "EggHatchPhase": {"action": "inspect_or_skip"},
    "ScanIvsPhase": {"action": "ignore"},
}


import random
from typing import Any, Dict, Optional


def resolve_phase_action(phase_name: str, *, settings: Optional[Dict[str, Any]] = None, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Resolve what to do for `phase_name` given settings and runtime state.

    - `settings` may contain user preferences like `want_capture` (bool), `use_map` (bool)
    - `state` may contain runtime info like `available_moves`, `party_status` etc.

    Returns a dict describing the action and any parameters.
    """
    if settings is None:
        settings = {}
    if state is None:
        state = {}

    entry = phases_skip_logic.get(phase_name)
    if not entry:
        return {"action": "unknown", "reason": "no_rule"}

    action = entry["action"]

    if action == "no_switch":
        return {"action": "no_switch"}

    if action == "start_run":
        return {"action": "press_start_combo", "combo": ["ENTER", "ENTER"]}

    if action == "choose_move":
        moves = state.get("available_moves") or ["move1"]
        # a simple heuristic: choose the first available move
        choice = moves[0]
        return {"action": "choose_move", "move": choice}

    if action == "learn_move_random":
        choices = entry.get("choices", [1, 2, 3, 4, 5])
        pick = random.choice(choices)
        if pick == 5:
            return {"action": "forget_move", "presses": 5}
        return {"action": "learn_move", "slot": pick}

    if action == "select_modifier_random":
        minv = entry.get("min", 1)
        maxv = entry.get("max", 3)
        pick = random.randint(minv, maxv)
        return {"action": "select_modifier", "index": pick}

    if action == "attempt_capture_conditional":
        want = settings.get("want_capture", False)
        if want:
            return {"action": "attempt_capture"}
        return {"action": "skip"}

    if action == "skip":
        return {"action": "skip"}

    if action == "smart_switch":
        # state is expected to have `party_status` list of booleans alive/dead
        party = state.get("party_status", [])
        # choose a random alive index different from current
        alive = [i for i, alive in enumerate(party) if alive]
        if not alive:
            return {"action": "no_switch_available"}
        pick = random.choice(alive)
        return {"action": "switch_to", "index": pick}

    if action == "backspace":
        return {"action": "press_backspace"}

    if action == "select_biome_first_only":
        use_map = settings.get("use_map", False)
        if not use_map:
            return {"action": "select_first_biome"}
        return {"action": "use_map_then_select_first"}

    if action == "inspect_or_skip":
        return {"action": "inspect_then_skip"}

    if action == "select_target_best_effort":
        targets = state.get("targets") or []
        if targets:
            return {"action": "select_target", "target": targets[0]}
        return {"action": "skip"}

    if action == "ignore":
        return {"action": "ignore"}

    return {"action": "unknown", "rule_action": action}


def demo():
    sample_phases = [
        "TitlePhase",
        "CommandPhase",
        "LearnMovePhase",
        "SelectModifierPhase",
        "AttemptCapturePhase",
        "EggSummaryPhase",
        "SelectBiomePhase",
        "SwitchPhase",
    ]
    settings = {"want_capture": False, "use_map": False}
    state = {"available_moves": ["Tackle", "Growl"], "party_status": [False, True, True], "targets": ["enemy1"]}
    for p in sample_phases:
        result = resolve_phase_action(p, settings=settings, state=state)
        print(f"Phase: {p} -> {result}")


if __name__ == "__main__":
    demo()
