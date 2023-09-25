element_status = {"Fire": (20, 37), "Water": (23, 38), "Air": (22, 39),
                  "Earth": (17, 8), "Poison": (18, 19)}


def check_element_effect(self):
    """Count elemental value and apply status"""
    for key in self.element_status_check:
        if key in element_status:
            self.element_status_check[key] = self.check_element_threshold(self.element_status_check[key],
                                                                          element_status[key][0],
                                                                          element_status[key][1])
    self.element_status_check = {key: value - self.timer if value > 0 else value for key, value in
                                 self.element_status_check.items()}
