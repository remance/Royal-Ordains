def use_skill(self, value):
    """ / in property indicate numeric value assignment instead of True"""
    if value["Prepare Animation"]:  # has animation to do first before performing skill animation
        return value["Prepare Animation"] | \
               {"next action": value["Property"] | {"Name": value["Move"], "moveset": True, "skill": True}}
    else:
        return value["Property"] | {"Name": value["Move"], "moveset": True, "skill": True}
