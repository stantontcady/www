

from flask import Flask, render_template

from credentials import secret_key


app = Flask(__name__)

class Photo:

    def __init__(self, basename):
        self.filename = '{0}.jpg'.format(basename)
        #self.datetime = ?


class WeekOfPhotos:

    def __init__(
            self, monday_photo=None, tuesday_photo=None, wednesday_photo=None, thursday_photo=None, friday_photo=None
    ):

        self.monday_photo = monday_photo
        self.tuesday_photo = tuesday_photo
        self.wednesday_photo = wednesday_photo
        self.thursday_photo = thursday_photo
        self.friday_photo = friday_photo


weeks_of_photos = (
    WeekOfPhotos(friday_photo=Photo('IMG_3299')),
    WeekOfPhotos(
        tuesday_photo=Photo('IMG_3336'),
        wednesday_photo=Photo('IMG_3343'),
        thursday_photo=Photo('IMG_3347'),
        friday_photo=Photo('IMG_3352')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3369'),
        tuesday_photo=Photo('IMG_3373'),
        wednesday_photo=Photo('IMG_3375'),
        thursday_photo=Photo('IMG_3378')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3390'),
        tuesday_photo=Photo('IMG_3392'),
        wednesday_photo=Photo('IMG_3395'),
        thursday_photo=Photo('IMG_3398'),
        friday_photo=Photo('IMG_3399')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3421'),
        tuesday_photo=Photo('IMG_3422'),
        wednesday_photo=Photo('IMG_3424'),
        thursday_photo=Photo('IMG_3425'),
        friday_photo=Photo('IMG_3427')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3439'),
        tuesday_photo=Photo('IMG_3440'),
        wednesday_photo=Photo('IMG_3441'),
        thursday_photo=Photo('IMG_3442'),
        friday_photo=Photo('IMG_3443')
    ),
    WeekOfPhotos(monday_photo=Photo('IMG_3445'), tuesday_photo=Photo('IMG_3446')),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3546'),
        tuesday_photo=Photo('IMG_3547'),
        wednesday_photo=Photo('IMG_3549'),
        thursday_photo=Photo('IMG_3551'),
        friday_photo=Photo('IMG_3553')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3556'),
        tuesday_photo=Photo('IMG_3558'),
        wednesday_photo=Photo('IMG_3561'),
        thursday_photo=Photo('IMG_3562'),
        friday_photo=Photo('IMG_3563')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3567'),
        tuesday_photo=Photo('IMG_3568'),
        wednesday_photo=Photo('IMG_3574'),
        thursday_photo=Photo('IMG_3578'),
        friday_photo=Photo('IMG_3580')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3581'),
        tuesday_photo=Photo('IMG_3582'),
        thursday_photo=Photo('IMG_3590'),
        friday_photo=Photo('IMG_3591')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3616'),
        tuesday_photo=Photo('IMG_3617'),
        wednesday_photo=Photo('IMG_3618'),
        thursday_photo=Photo('IMG_3620'),
        friday_photo=Photo('IMG_3622')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3645'),
        tuesday_photo=Photo('IMG_3646'),
        wednesday_photo=Photo('IMG_3647'),
        thursday_photo=Photo('IMG_3649'),
        friday_photo=Photo('IMG_3653')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3675'),
        tuesday_photo=Photo('IMG_3676'),
        wednesday_photo=Photo('IMG_3680'),
        friday_photo=Photo('IMG_3685')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3732'),
        tuesday_photo=Photo('IMG_3733'),
        wednesday_photo=Photo('IMG_3735'),
        thursday_photo=Photo('IMG_3736'),
        friday_photo=Photo('IMG_3738')
    ),
    WeekOfPhotos(
        tuesday_photo=Photo('IMG_3814'),
        wednesday_photo=Photo('IMG_3816'),
        thursday_photo=Photo('IMG_3819'),
        friday_photo=Photo('IMG_3821')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3876'),
        tuesday_photo=Photo('IMG_3880'),
        wednesday_photo=Photo('IMG_3884'),
        thursday_photo=Photo('IMG_3897'),
        friday_photo=Photo('IMG_3901')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3924'),
        tuesday_photo=Photo('IMG_3929'),
        wednesday_photo=Photo('IMG_3935'),
        thursday_photo=Photo('IMG_3940'),
        friday_photo=Photo('IMG_3944')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_3992'), tuesday_photo=Photo('IMG_4002'), wednesday_photo=Photo('IMG_4009')
    ),
    WeekOfPhotos(),
    WeekOfPhotos(),
    WeekOfPhotos(
        tuesday_photo=Photo('IMG_5001'),
        wednesday_photo=Photo('IMG_5009'),
        thursday_photo=Photo('IMG_5011'),
        friday_photo=Photo('IMG_5015')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_5042'),
        tuesday_photo=Photo('IMG_5043'),
        wednesday_photo=Photo('IMG_5049'),
        thursday_photo=Photo('IMG_5052'),
        friday_photo=Photo('IMG_5054')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_5057'),
        tuesday_photo=Photo('IMG_5061'),
        thursday_photo=Photo('IMG_5076'),
        friday_photo=Photo('IMG_5077')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_5094'),
        tuesday_photo=Photo('IMG_5095'),
        wednesday_photo=Photo('IMG_5096'),
        thursday_photo=Photo('IMG_5101'),
        friday_photo=Photo('IMG_5102')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_5114'),
        tuesday_photo=Photo('IMG_5117'),
        wednesday_photo=Photo('IMG_5118'),
        thursday_photo=Photo('IMG_5121'),
        friday_photo=Photo('IMG_5124')
    ),
    WeekOfPhotos(wednesday_photo=Photo('IMG_5148'), thursday_photo=Photo('IMG_5149')),
    WeekOfPhotos(
        monday_photo=Photo('IMG_5158'), tuesday_photo=Photo('IMG_5159'), wednesday_photo=Photo('IMG_5160')
    ),
    WeekOfPhotos(
        monday_photo=Photo('IMG_5189'),
        wednesday_photo=Photo('IMG_5202'),
        thursday_photo=Photo('IMG_5203'),
        friday_photo=Photo('IMG_5204')
    ),
    WeekOfPhotos(
        tuesday_photo=Photo('IMG_5320'),
        wednesday_photo=Photo('IMG_5322'),
        thursday_photo=Photo('IMG_5324'),
        friday_photo=Photo('IMG_5326')
    ),
    WeekOfPhotos(thursday_photo=Photo('IMG_5345'), friday_photo=Photo('IMG_5345')),
    WeekOfPhotos(),
    WeekOfPhotos(wednesday_photo=Photo('IMG_5479'), thursday_photo=Photo('IMG_5480')),
    WeekOfPhotos(
        monday_photo=Photo('IMG_5494'),
        wednesday_photo=Photo('IMG_5497'),
        thursday_photo=Photo('IMG_5499'),
        friday_photo=Photo('IMG_5502')
    ),
    WeekOfPhotos(tuesday_photo=Photo('IMG_5512')),
    WeekOfPhotos(
        tuesday_photo=Photo('IMG_5544'),
        wednesday_photo=Photo('IMG_5545'),
        thursday_photo=Photo('IMG_5546'),
        friday_photo=Photo('IMG_5547')
    ),
    WeekOfPhotos(monday_photo=Photo('IMG_5559'))
)


@app.route('/daily_photo/grid')
def daily_photo_grid():
    return render_template('daily_photo_grid.html', weeks_of_photos=enumerate(weeks_of_photos))


@app.route('/daily_photo')
def daily_photo():
    return render_template('daily_photo.html')
