def check_element_threshold(self, element, tier1status, tier2status):
    """apply elemental status effect when reach elemental threshold"""
    if element > 50:  # apply tier 1 status
        self.apply_status(tier1status)
        if element > 100:  # apply tier 2 status
            self.apply_status(tier2status)
            element = 0  # reset elemental count
    elif element < 0:
        element = 0
    return element
