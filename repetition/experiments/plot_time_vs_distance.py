
from datetime import datetime, timedelta
from math import floor

from fitparse import FitFile
import cairo

path = '3558695020.fit'

fit_file = FitFile(path)

timestamp_to_distance_mapping = {
    record.get_value('timestamp'): record.get_value('distance') for record in fit_file.get_messages(name='record')
}

start_time = datetime(2019, 4, 15)
end_time = datetime(2019, 4, 16)

timestamp = start_time

height = 4500

surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 24*60*10, height)
ctx = cairo.Context(surface)

ctx.set_line_width(2)
ctx.set_source_rgb(0.7, 0.2, 0.0)
ctx.move_to(0, height)
prev_y = None

while timestamp < end_time:

    seconds_elapsed = (timestamp - start_time).seconds/10

    distance = timestamp_to_distance_mapping.get(timestamp)

    # print(ctx.get_current_point())
    if distance is not None:
        y = distance/10
        ctx.line_to(seconds_elapsed, height-y)
        ctx.stroke()
        ctx.move_to(seconds_elapsed, height-y)

    else:
        ctx.move_to(seconds_elapsed, height)

    timestamp += timedelta(seconds=1)


surface.write_to_png("plot.png")
