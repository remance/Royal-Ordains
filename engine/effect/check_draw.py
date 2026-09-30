def check_draw(self):
    battle_camera_drawer = self.battle_camera_drawer
    if self.rect.colliderect(self.camera.rect):
        if self not in battle_camera_drawer:
            battle_camera_drawer.add(self)
    elif self in battle_camera_drawer:
        battle_camera_drawer.remove(self)
