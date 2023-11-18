from pygame.joystick import Joystick


def add_joystick(self, event):
    joy = Joystick(event.device_index)
    self.joysticks[joy.get_instance_id()] = joy
    joy_name = joy.get_name()
    for name in self.joystick_bind_name:
        if name in joy_name:  # find common name
            self.joystick_name[joy.get_instance_id()] = name
    if joy.get_instance_id() not in self.joystick_name:
        self.joystick_name[joy.get_instance_id()] = "Other"

    for player in self.player_key_control:  # check for player with joystick control but no assigned yet
        if self.player_key_control[player] == "joystick" and player not in self.player_joystick:
            # assign new joystick to player with joystick control setting
            self.player_joystick[player] = joy.get_instance_id()
            self.joystick_player[joy.get_instance_id()] = player
            break  # only one player get assigned
