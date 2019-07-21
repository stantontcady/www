

from cairo import PDFSurface, Context
from math import atan, ceil, cos, pi, sin
from IPython import embed



height = 160
width = 260
canvas_padding = 15

dot_radius = 0.5

surface = PDFSurface('dot_pattern_1.pdf', width+2*canvas_padding, height+2*canvas_padding)
ctx = Context(surface)

ctx.rectangle(0, 0, width + 2*canvas_padding, height + 2*canvas_padding)
ctx.set_source_rgb(1, 1, 1)
ctx.fill()

num_full_arc_rings = 8
max_num_filler_arc_rings = 9
dot_padding = 1
ring_padding = 1

pattern_radius = num_full_arc_rings*(2*dot_radius + ring_padding)

max_arc_radius = (num_full_arc_rings - 1)*(dot_radius*2 + ring_padding)


def draw_dot(x, y):

    ctx.arc(x, y, dot_radius, 0, 2*pi)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()


def draw_arc_of_dots(arc_radius, arc_start_angle, arc_end_angle, x_pattern_center, y_pattern_center):

    arc_angle = arc_end_angle - arc_start_angle

    arc_length = arc_radius*arc_angle

    num_dots = ceil(arc_length/(2*dot_radius + dot_padding))

    angle_increment = arc_angle/num_dots

    for dot_idx in range(num_dots+1):

        angle = arc_start_angle + angle_increment*dot_idx

        draw_dot(x_pattern_center + arc_radius*cos(angle), y_pattern_center - arc_radius*sin(angle))


for pattern_row_idx in range(10):

    x_pattern_center = 0 + canvas_padding
    y_pattern_center = 0 + canvas_padding + (pattern_row_idx + 1)*pattern_radius

    for ring_idx in range(0, max(num_full_arc_rings, max_num_filler_arc_rings)):

        if ring_idx == 0:
            draw_dot(x_pattern_center, y_pattern_center)

        else:

            arc_radius = ring_idx*(dot_radius*2 + ring_padding)
            max_arc_angle = atan(arc_radius/max_arc_radius)

            if ring_idx < num_full_arc_rings:
                draw_arc_of_dots(
                    arc_radius,
                    pi/2-0.625*max_arc_angle,
                    pi/2,
                    x_pattern_center,
                    y_pattern_center
                )

    for pattern_col_idx in range(15):

        x_pattern_center = 0 + canvas_padding + (pattern_col_idx + 1)*pattern_radius
        y_pattern_center = 0 + canvas_padding + (pattern_row_idx + 1)*pattern_radius

        for ring_idx in range(max(num_full_arc_rings, max_num_filler_arc_rings)):

            if ring_idx == 0:
                draw_dot(x_pattern_center, y_pattern_center)

            else:

                arc_radius = ring_idx*(dot_radius*2 + ring_padding)

                if pattern_col_idx % 2:

                    max_arc_angle = atan(arc_radius/max_arc_radius)

                    half_main_arc_angle = 0.3*max_arc_angle

                    if ring_idx < num_full_arc_rings:
                        draw_arc_of_dots(
                            arc_radius,
                            pi/2-0.625*max_arc_angle,
                            pi/2+0.625*max_arc_angle,
                            x_pattern_center,
                            y_pattern_center
                        )

                    # if ring_idx > 3:
                    #     draw_arc_of_dots(
                    #         arc_radius,
                    #         pi/2+half_main_arc_angle+0.1,
                    #         pi/2+half_main_arc_angle+0.1+max_arc_angle*0.15,
                    #         x_pattern_center,
                    #         y_pattern_center
                    #     )

                    # draw_arc_of_dots(arc_radius, pi/2-half_arc_angle, pi/2, x_pattern_center, y_pattern_center)
                    # draw_arc_of_dots(arc_radius, pi/2, pi/2+half_arc_angle, x_pattern_center, y_pattern_center)

                elif ring_idx < num_full_arc_rings:
                    draw_arc_of_dots(arc_radius, 0, pi, x_pattern_center, y_pattern_center)

    x_pattern_center += pattern_radius
    for ring_idx in range(0, max(num_full_arc_rings, max_num_filler_arc_rings)):

        if ring_idx == 0:
            draw_dot(x_pattern_center, y_pattern_center)

        else:

            arc_radius = ring_idx*(dot_radius*2 + ring_padding)
            max_arc_angle = atan(arc_radius/max_arc_radius)

            if ring_idx < num_full_arc_rings:
                draw_arc_of_dots(
                    arc_radius,
                    pi/2,
                    pi/2+0.625*max_arc_angle,
                    x_pattern_center,
                    y_pattern_center
                )

# for row_idx in range(40):
#
#     for col_idx in range(40):
#
#         x = canvas_padding + dot_radius*(1+row_idx) + row_idx*(dot_radius*2 + dot_padding)
#         y = canvas_padding + dot_radius*(1+col_idx) + col_idx*(dot_radius*2 + dot_padding)
#
#         ctx.arc(x, y, dot_radius, 0, 2*pi)
#         ctx.set_source_rgb(0, 0, 0)
#         ctx.fill()

# surface.write_to_png("# dot_pattern_1.pdf")
