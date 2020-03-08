from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed

APP = Flask(__name__)

photos = UploadSet('photos', IMAGES) # IMAGES, and any other file type group (such as TEXT) is a tuple with file terminations. You can define your own or combine the ones existent in Flask Uploads

# The "PHOTOS" in the command below derived from the 'photos' in the command above.
APP.config['UPLOADED_PHOTOS_DEST'] = 'pictures'
APP.config['UPLOADED_PHOTOS_ALLOW'] = ['txt'] # Will accept txts too
APP.config['UPLOADED_PHOTOS_DENY'] = ['bmp'] # Won't accept bmps, even though they're in the default image types
APP.config['UPLOADS_DEFAULT_DEST'] = 'other' # Files upload through an upload set that has no dest defined will be saved in what's specified here.

configure_uploads(APP, photos)


@APP.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'thefile' in request.files:
        try:
            image_filename = photos.save(request.files['thefile'])
            #return f'<h1>{photos.path(image_filename)} has been uploaded</h1>'
            return f'<h1>{photos.url(image_filename)} has been uploaded</h1>'

        except UploadNotAllowed:
            return "This file typo' file ain't allowed!"

    return render_template('upload.html')


if __name__ == '__main__':
    APP.run(debug=True)

