

import cairo



square_size = 200
padding = 20
stroke_width = 3

start_col_idx = 1
start_row_idx = 0

num_cols = 52
num_rows = 7

width = num_cols*square_size + (num_cols+1)*padding
height = num_rows*square_size + (num_rows+1)*padding


surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
ctx = cairo.Context(surface)


ctx.rectangle(0, 0, width, height)
ctx.set_source_rgb(1, 1, 1)
ctx.fill()

for row_idx in range(num_rows):

    for col_idx in range(num_cols):

        if row_idx == start_row_idx and col_idx < start_col_idx:
            continue

        y = (1+row_idx)*padding + row_idx*square_size
        x = (1+col_idx)*padding + col_idx*square_size

        ctx.rectangle(x, y, square_size, square_size)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(stroke_width)
        ctx.stroke()

surface.write_to_png("grid_of_squares.png")
