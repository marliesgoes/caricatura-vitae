from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg'}
ALLOWED_EXTENSIONS_RESUME = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        resume_file = request.files.get('resume')
        image_file = request.files.get('image')

        # Initialize filenames
        resume_filename, image_filename = None, None

        if resume_file and allowed_file(resume_file.filename, ALLOWED_EXTENSIONS_RESUME):
            resume_filename = secure_filename(resume_file.filename)
            resume_filepath = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
            resume_file.save(resume_filepath)
            # Here you should add the resume parsing logic

        if image_file and allowed_file(image_file.filename, ALLOWED_EXTENSIONS_IMAGE):
            image_filename = secure_filename(image_file.filename)
            image_filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_filepath)
            # Process image if necessary

        # After processing both files, you can call Dalle API and generate the image based on the resume content
        # Call Dalle API
        # Save the Dalle-generated image

        return render_template('display.html', user_image=image_filename, dalle_image='dalle_generated_image.png')

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
