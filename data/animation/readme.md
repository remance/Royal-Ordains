Animation

This folder contains list of animation for each direction.

The animation file need to be in this structure:
Animation name, each p*number* (upto p4) parts, effect, special, frame and animation properties

Animation name should be like this

Each animation part need to be in this format:
race/type,direction name, part name, position x, position y, angle, flip (0=none,1=hori,2=verti,3=both), layer, scale (1
for default)

THERE MUST BE NO SPACE BETWEEN COMMA IN ANY VALUE

The position is based on the default side before any flip (face right or left).

layer value is similar to pygame layer, the higher value get drew first and lower value get drew later and above the higher value layer. Layer must start from 0.
