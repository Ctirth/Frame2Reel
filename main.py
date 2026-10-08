from flask import Flask, render_template, request, redirect, url_for
import uuid
from werkzeug.utils import secure_filename
import os

# Import your generate functions
from generate_process import text_to_audio, create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/reels', exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    myid = str(uuid.uuid1())  # Generate unique ID for this upload
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], myid)
    os.makedirs(folder_path, exist_ok=True)

    if request.method == "POST":
        desc = request.form.get("text", "").strip()
        input_files = []

        # Handle uploaded files
        for key, file in request.files.items():
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder_path, filename))
                input_files.append(filename)

        # Save description
        with open(os.path.join(folder_path, "desc.txt"), "w", encoding="utf-8") as f:
            f.write(desc)

        # Create input.txt for ffmpeg
        input_txt_path = os.path.join(folder_path, "input.txt")
        with open(input_txt_path, "w", encoding="utf-8") as f:
            for fl in input_files:
                f.write(f"file '{fl}'\nduration 1\n")

        # Generate audio and create reel immediately
        if text_to_audio(myid):
            create_reel(myid)
        else:
            print(f"⚠️ Could not generate audio for {myid}")

        return redirect(url_for("gallery"))

    return render_template("create.html", myid=myid)


@app.route("/gallery")
def gallery():
    reels_folder = "static/reels"
    reels = [f for f in os.listdir(reels_folder) if f.endswith(".mp4")]
    return render_template("gallery.html", reels=reels)


if __name__ == "__main__":
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
