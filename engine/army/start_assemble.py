def start_assemble(self):
    self.assembling_followers = {key: {index: for index, item in enumerate(value) if not item[1]}
    for key, value in self.army_followers.items()}
