import math


def blit_center(surf, surf2, pos):
    x = int(surf2.get_width()/2)
    y = int(surf2.get_height()/2)
    surf.blit(surf2, (pos[0]-x, pos[1]-y))


def swap_color(img, old_c, new_c, e_colorkey):
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    surf.set_colorkey(e_colorkey)
    return surf


def advance(loc, angle, amt):
    new_loc = loc.copy()
    new_loc[0] += math.cos(math.radians(angle)) * amt
    new_loc[1] += math.sin(math.radians(angle)) * amt
    return new_loc


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
