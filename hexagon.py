"""
Script to generate hexagon in .svg and dxf for a periodic table

author: Devillez Louis
"""
import json
import math
import os
import subprocess
import cairo
from helper import draw_text



# Width of an hexagon
WIDTH_HEXA = 34.2
# length of the side on one hexagon
side_hexa = WIDTH_HEXA / math.sqrt(3)

# Spacing between the hexagon
SPACING = 0.7

# diameter of the vial
D_VIAL = 12.8


# Spacing
SPACE_VIAL = 3.8
SPACE_NAME_SYMBOL = 7.3
SPACE_SYMBOL_NUMBER = 7.3

# Maximum number of hexagons on a line
MAX_N_LINE = 5

def draw_hexagon(cr, x, y):
    """
    cr: context surface of Cairo
    x: x coordinate of the center of the hexagon
    y: y coordinate of the center of the hexagon
    """

    # Move to first side
    cr.move_to(x + side_hexa, y)

    # Do all the sides
    for i in range(0,6+1):
        x_hexa = x + side_hexa * math.cos(i * 2 * math.pi/6 + math.pi/6)
        y_hexa = y + side_hexa * math.sin(i * 2 * math.pi/6 + math.pi/6)
        if i == 0:
            cr.move_to(x_hexa, y_hexa)
        else:
            cr.line_to(x_hexa, y_hexa)
    cr.close_path()
    cr.stroke()

    # Draw the hole for the vial
    y_circle = y + side_hexa - SPACE_VIAL - D_VIAL/2
    cr.arc(x, y_circle, D_VIAL/2, 0, 2*math.pi)
    cr.close_path()
    cr.stroke()

    # Draw the name of the element
    y_name = y_circle - SPACE_VIAL - D_VIAL/2
    text = elem["name"]
    cr.set_font_size(4)
    draw_text(x,y_name,text,cr)

    # Draw the symbol of the element
    y_symbol = y_name - SPACE_NAME_SYMBOL
    cr.set_font_size(11)
    text = elem["symbol"]
    draw_text(x,y_symbol,text,cr)

    # Draw the number of the element
    y_number = y_symbol - SPACE_SYMBOL_NUMBER
    cr.set_font_size(5)
    text = str(elem["number"])
    draw_text(x,y_number,text,cr)


def get_cat(elem):
    """
    elem: an dict representing an element
    """

    # Sanitize the string
    elem_cat = elem["category"].replace("unknown, probably ", "").replace("unknown, predicted to be ", "")

    # For its own category
    if elem_name == "hydrogen":
        elem_cat = "hydrogen"

    # Last metalloid are poor metal
    if elem_cat == "metalloid" and elem["block"] == "p":
        elem_cat = "poor metal"

    # Change the name
    if "nonmetal" in elem_cat:
        elem_cat = "non metal"

    if elem["group"] == 12 and elem_cat != "non metal":
        elem_cat = "poor metal"

    if elem_name == "nihonium":
        elem_cat = "poor metal"

    # Split the post-transition metal
    if elem_cat == "post-transition metal":
        if elem_name in ["aluminium", "gallium", "indium", "tin", "thallium", "lead"]:
            elem_cat = "poor metal"
        else:
            elem_cat = "non metal"

    # Correct the wrong one
    if elem["number"] in [5, 14, 33, 52, 85]:
        elem_cat = "non metal"

    if elem["number"] in [50, 82, 83, 84, 114, 115, 116]:
        elem_cat = "poor metal"

    # Sanitize a bit more
    return elem_cat.replace(" ", "_")



# Open the json
with open("./periodic-table-lookup.json", encoding="utf8") as f:
    data = json.load(f)

# Create a categories dict containing the name of the elements in the category
dict_of_cat = {}
for elem_name in data["order"]:
    elem_cat = get_cat(data[elem_name])
    if elem_cat not in dict_of_cat:
        dict_of_cat[elem_cat] = [elem_name]
    else:
        dict_of_cat[elem_cat].append(elem_name)


# Create directory if needed
if not os.path.isdir("svg/"):
    os.mkdir("svg/")

if not os.path.isdir("dxf/"):
    os.mkdir("dxf/")

# For each category
for cat, elems in dict_of_cat.items():

    # Get the number of elements
    n_elem = len(elems)

    # Get the number of row and lines
    n_row = math.ceil(n_elem / MAX_N_LINE)
    n_col = min(MAX_N_LINE,n_elem)

    # Compute the width and height of the canva
    height = (0.25 + n_row * 0.75) * 2*(side_hexa + SPACING)
    width = (n_col + 0.5) * (WIDTH_HEXA + SPACING)

    # Create a cairo surface
    with cairo.SVGSurface(f"svg/{cat}.svg", width, height) as surface:
        # Create a context for this surface
        cr = cairo.Context(surface)

        # Set units to mm
        surface.set_document_unit(6)

        # Set font
        cr.set_font_size(10)
        cr.select_font_face("Latin Modern Sans Demi Cond",
                        cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_NORMAL)

        # Set linewidth
        cr.set_line_width(0.5)

        # For each element of the category
        for idx_elem, elem_name in enumerate(elems):
            # Get the data
            elem = data[elem_name]

            # get its row and number
            n_x = idx_elem % MAX_N_LINE
            n_y = math.floor(idx_elem / MAX_N_LINE)

            # Get the position
            x_elem = n_x*(WIDTH_HEXA + SPACING) + WIDTH_HEXA/2
            y_elem = 0.75 * n_y * (2 * side_hexa + SPACING) + side_hexa

            if n_y % 2 == 1:
                x_elem += (WIDTH_HEXA + SPACING) / 2

            # draw the hexagon
            draw_hexagon(cr, x_elem, y_elem)
    subprocess.run(["inkscape", f"svg/{cat}.svg", "-o", f"dxf/{cat}.dxf"])
