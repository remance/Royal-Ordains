import numpy as np
from PIL import Image

color_list = []
im = Image.open("world.png")
rgb_im = np.array(im)
for row in rgb_im:
    for col in row:
        rgb = col
        color_list.append((int(rgb[0]), int(rgb[1]), int(rgb[2])))

color_list = list(set(color_list))
# print(color_list[0])
# print(len(color_list))

# from PIL import ImageColor
#
# import os
# import csv
# check = []
# with open("region.csv",
#           encoding="utf-8", mode="r") as edit_file:
#     rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
#     header = rd[0]
#     for index, row in enumerate(rd[1:]):
#         check.append(ImageColor.getrgb("#" + row[1]))
# edit_file.close()
#
# print(len(color_list), len(check), len(set(check)))
#
# from collections import Counter
#
# # Use Counter to count
# #the occurrences of each element in the list
# counts = Counter(check)
# duplicates = [item for item, count in counts.items() if count > 1]
# print(['#%02x%02x%02x' % item for item in duplicates], "asd")
#
# for item in color_list:
#     if item not in check:
#         print(item)
#
# print("hmasd")
# for item in check:
#     if item not in color_list:
#         print('#%02x%02x%02x' % item, item)
