def check_prepare_action(self, value):
    """Assuming attack/special button related is always last button"""
    if "Weak" in value["Buttons"]:
        action = self.weak_attack_command_action
    elif "Strong" in value["Buttons"]:
        action = self.strong_attack_command_action
    elif "Special" in value["Buttons"]:
        action = self.special_command_action

    if value["Prepare Animation"]:  # has animation to do first before performing main animation
        return value["Prepare Animation"] | \
                         {"next action": value["Property"] | action | {"no prepare": True}}
    return action

