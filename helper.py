

def draw_text(X,Y,text,cr):
    """
    X: x position of the center of the text
    Y: y position of the center of the text
    text: string representing the text
    cr: Cairo context to draw the text
    """
    x_bearing, y_bearing, width, height, x_advance, y_advance = \
    cr.text_extents(text)
    x = - (width / 2 + x_bearing)
    y = 0.5 - (height / 2 + y_bearing)

    cr.move_to(x + X, y + Y)
    cr.show_text(text)
