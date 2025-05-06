from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from .models import Signupdb
from .models import DetectionHistory
import cv2
from django.http import StreamingHttpResponse
from ultralytics import YOLO
import cvzone
import math
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import uuid
import time

# Load YOLO model once
model = YOLO(r"C:\Users\POOJA\runs\detect\train\weights\best.pt")
class_names = model.names

def HomeView(request):
    return render(request,'home.html')

def Logines(request):

        return render(request,'Login_page.html')


def SignUp(request):
    if request.method == "POST":
        uname = request.POST.get('username')
        email = request.POST.get("email")
        password = request.POST.get("password")
        password1 = request.POST.get("password1")

        if password != password1:
            return HttpResponse("Passwords do not match!")

        my_user = Signupdb(
            Username=uname,
            Email=email,
            Password=password,
            ConfirmPassword=password1
        )
        my_user.save()

        # Redirect to login page after signup
        return redirect('logins')

    return render(request, "SignUp_page.html")

def About(request):
    return render(request, "About_page.html")

def Mainpage(request):
    return render(request, "Main_page.html")


def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame, stream=True)
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                label = f'{class_names[cls]} {conf}'
                cvzone.cornerRect(frame, (x1, y1, w, h))
                cvzone.putTextRect(frame, label, (x1, y1 - 10))

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def live_feed_view(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def live_detection_page(request):
    return render(request, 'live_detection.html')

# Process Video function
def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)

    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    max_duration_sec = 30
    max_frames = int(fps * max_duration_sec)

    frame_count = 0

    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        results = model(frame)

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model.names[int(box.cls[0])]
                conf = round(float(box.conf[0]), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        out.write(frame)

    cap.release()
    out.release()
    print(f"✅ Finished processing {frame_count} frames (max 30 seconds).")


def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        filename = fs.save(video_file.name, video_file)
        input_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

        output_filename = 'processed_' + filename
        output_path = os.path.join(settings.MEDIA_ROOT, 'outputs', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cap = cv2.VideoCapture(input_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            results = model(frame, stream=True)
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = model.names[int(box.cls[0])]
                    conf = round(float(box.conf[0]), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} {conf}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            out.write(frame)

        cap.release()
        out.release()

        DetectionHistory.objects.create(
            user=request.session.get('username', 'anonymous'),
            input_file='uploads/' + filename,
            output_file='outputs/' + output_filename,
            detection_type='video'
        )

        return render(request, 'video_result.html', {
            'video_url': settings.MEDIA_URL + 'outputs/' + output_filename
        })

    return render(request, 'upload_video.html')


def video_result(request):
    return render(request, 'video_result.html')

from .models import DetectionHistory

def detect_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Save the uploaded file
        image_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        input_path = fs.path(filename)

        # Read image with OpenCV
        img = cv2.imread(input_path)

        if img is None:
            return render(request, 'upload_Image.html', {'error': 'Could not read uploaded image.'})

        # Run detection
        results = model(img)

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model.names[int(box.cls[0])]
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Save processed image
        result_filename = 'result_' + filename
        result_path = os.path.join(settings.MEDIA_ROOT, result_filename)
        cv2.imwrite(result_path, img)

        # ✅ Now save detection history
        if 'username' in request.session:
            user = request.session['username']
        else:
            user = 'anonymous'

        DetectionHistory.objects.create(
            user=user,
            input_file=filename,        # only file name, Django knows MEDIA_ROOT
            output_file=result_filename,
            detection_type='image'
        )

        return render(request, 'upload_Image.html', {
            'image_url': settings.MEDIA_URL + result_filename
        })

    return render(request, 'upload_Image.html')

def Contactpage(request):
    return render(request, "Contact_page.html")
