from flask import Flask, request, render_template, flash, redirect
from werkzeug.utils import secure_filename
from openai import OpenAI
import requests
import random
import imghdr
import os
import PyPDF2
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"

# Configuration
UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS_RESUME = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        resume_file = request.files.get("resume")
        image_file = request.files.get("image")
        if not resume_file or not image_file:
            flash("Both resume and image files are required!", "error")
            return redirect(request.url)

        if resume_file and allowed_file(
            resume_file.filename, ALLOWED_EXTENSIONS_RESUME
        ):
            resume_filename = secure_filename(resume_file.filename)
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
            resume_filepath = os.path.join(app.config["UPLOAD_FOLDER"], resume_filename)
            resume_file.save(resume_filepath)

            # Parse PDF resume
            extracted_text = parse_pdf(resume_filepath)
            # Remove personal information from extracted text
            anonymized_text = anonymize_info(extracted_text)

            prompt_gpt = f"""
            Concisely describe the person whom the following resume might belong to.

            RESUME: {anonymized_text}
            """
            print(prompt_gpt)
            print()

            description = call_gpt(prompt_gpt)

            prompt_dalle = f"""
            {description}
            Create a photorealistic portrait of the described person. White uniform background, warm lights. No text.
            """
            print(prompt_dalle)

            # Call Dalle API
            image_url = call_dalle(prompt_dalle)
            # Save the Dalle-generated image
            download_image(image_url, "todo.png")

            return render_template(
                "display.html",
                user_image="uploaded_image.png",
                dalle_image=resume_filename,
            )

    return render_template("upload.html")


def parse_pdf(filepath):
    with open(filepath, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def download_image(image_url: str, filename: str):
    response = requests.get(image_url)
    response.raise_for_status()  # To ensure the request was successful

    # Determine the image type
    image_type = imghdr.what(None, h=response.content)
    if image_type is None:
        raise ValueError("Could not determine the image type.")

    # Append the appropriate suffix if not already present
    if not filename.lower().endswith(f".{image_type}"):
        filename += f".{image_type}"

    with open(filename, "wb") as f:
        f.write(response.content)

    print(f"Image successfully saved to {filename}.")


def call_dalle(
    prompt,
    model="dall-e-3",
    size="1024x1024",
    quality="standard",
    mock_gpt_call=False,
):
    if mock_gpt_call:
        print(f"Mocking DallE call...")
        return "https://github.com/marliesgoes/marliesgoes/blob/main/fake_dalle.png?raw=true"

    print(f"Calling {model}...")

    response = client.images.generate(
        model=model, prompt=prompt, size=size, quality=quality
    )
    return response.data[0].url


def call_gpt(prompt, model="gpt-4-0125-preview", mock_gpt_call=False):
    if mock_gpt_call:
        print(f"Mocking GPT call...")
        return random.choice(["CORRECT", "FALSE", "UNSURE"])
    else:
        print(f"Calling {model}...")
        messages = [{"role": "user", "content": prompt}]

        response = client.chat.completions.create(model=model, messages=messages)
        result = response.choices[0].message.content.strip()
    return result


def anonymize_info(text):
    # Implement logic to anonymize personal information in text
    return text


if __name__ == "__main__":
    app.run(debug=True)
