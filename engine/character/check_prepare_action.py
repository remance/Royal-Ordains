def check_prepare_action(self, value):
    """Assuming attack/special button related is always last button"""
    if "Weak" in value["Buttons"]:
        action = self.weak_attack_command_action
    elif "Strong" in value["Buttons"]:
        action = self.strong_attack_command_action
    elif "Special" in value["Buttons"]:
        action = self.special_command_action
    else:  # other type of moveset like slide and tackle with no specific button command assign
        action = self.current_action

    if value["After Animation"]:
        action = action | {"next action": value["After Animation"] | {"no prepare": True, "sub action": True}}

    if value["Prepare Animation"]:  # has animation to do first before performing main animation
        return value["Prepare Animation"] | \
               {"sub action": True,
                "next action": value["Property"] | action | self.current_moveset["Property"] | {"no prepare": True}}
    return action  # not add property here, will be added later
