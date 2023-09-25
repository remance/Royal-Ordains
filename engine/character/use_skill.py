def use_skill(self, value):
    """ / in property indicate numeric value assignment instead of True"""
    if value["Prepare Animation"]:  # has animation to do first before performing skill animation
        return value["Prepare Animation"] | \
               {"next action": {item: True for item in value["Property"] if "/" not in item} | \
                               {item.split("/")[0]: float(item.split("/")[1]) for item in value["Property"]
                                if "/" in item} | {"Name": value["Move"], "moveset": True, "skill": True}}
    else:
        return {item: True for item in value["Property"] if "/" not in item} | \
               {item.split("/")[0]: float(item.split("/")[1]) for item in value["Property"]
                if "/" in item} | {"Name": value["Move"], "moveset": True, "skill": True}

