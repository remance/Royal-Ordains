from pygame.sprite import LayeredUpdates, Sprite


class ReversedLayeredUpdates(LayeredUpdates):
    """
    Layer updater that prioritise lower layer first
    """
    def __init__(self):
        LayeredUpdates.__init__(self)

    def add_internal(self, sprite, layer=None):
        """
        Change add internal to order the sprite list from top to bottom instead of the original bottom to top
        """
        LayeredUpdates.add_internal(self, sprite, layer)
        self._spritelist.reverse()  # revert to top to bottom

    def remove(self, *sprites):
        """remove sprite(s) from group

        Group.remove(sprite, list, or group, ...): return None

        Removes a sprite or sequence of sprites from a group.

        """
        # This function behaves essentially the same as Group.add. It first
        # tries to handle each argument as an instance of the Sprite class. If
        # that fails, then it tries to handle the argument as an iterable
        # object. If that fails, then it tries to handle the argument as an
        # old-style sprite group. Lastly, if that fails, it assumes that the
        # normal Sprite methods should be used.
        for sprite in sprites:
            if isinstance(sprite, Sprite):
                sprite.event = False
                sprite.event_press = False
                sprite.event_hold = False
                sprite.mouse_over = False
                if self.has_internal(sprite):
                    self.remove_internal(sprite)
                    sprite.remove_internal(self)
            else:
                try:
                    self.remove(*sprite)
                except (TypeError, AttributeError):
                    if hasattr(sprite, "_spritegroup"):
                        for spr in sprite.sprites():
                            spr.event = False
                            spr.event_press = False
                            spr.event_hold = False
                            spr.mouse_over = False
                            if self.has_internal(spr):
                                self.remove_internal(spr)
                                spr.remove_internal(self)
                    elif self.has_internal(sprite):
                        sprite.event = False
                        sprite.event_press = False
                        sprite.event_hold = False
                        sprite.mouse_over = False
                        self.remove_internal(sprite)
                        sprite.remove_internal(self)
