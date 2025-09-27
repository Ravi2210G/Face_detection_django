import io
import base64
from PIL import Image
import numpy as np
import cv2

from django.shortcuts import render
from .forms import UploadImageForm

def detect_faces_in_image(pil_image):
    # Convert PIL image to OpenCV BGR
    open_cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

    # Use OpenCV's built-in Haar cascade (no external download)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # draw rectangles
    for (x, y, w, h) in faces:
        cv2.rectangle(open_cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # convert back to PIL RGB
    result_rgb = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
    pil_result = Image.fromarray(result_rgb)
    return pil_result, faces

def index(request):
    result_img_b64 = None
    faces = []
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            pil_image = Image.open(form.cleaned_data['image']).convert('RGB')
            result_pil, faces = detect_faces_in_image(pil_image)

            # convert result image to base64 to embed in HTML
            buffered = io.BytesIO()
            result_pil.save(buffered, format='JPEG')
            img_str = base64.b64encode(buffered.getvalue()).decode()
            result_img_b64 = 'data:image/jpeg;base64,' + img_str
    else:
        form = UploadImageForm()
    return render(request, 'detector/index.html', {
        'form': form,
        'result_img': result_img_b64,
        'faces_count': len(faces),
    })

camera = cv2.VideoCapture(0)

def gen_frames():
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    while True:
        success, frame = camera.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def live(request):
    return StreamingHttpResponse(gen_frames(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


import cv2
from django.shortcuts import render
from django.http import StreamingHttpResponse

# -------------------------
# 1️⃣ Live webcam streaming
# -------------------------
def gen_frames():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.1, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    cap.release()

# Video streaming response
def live_feed(request):
    return StreamingHttpResponse(gen_frames(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

# Live page
def live_page(request):
    return render(request, 'detector/live.html')

