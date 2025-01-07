from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from tasks.tasks import generate_hls

@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        # Save the uploaded video file
        fs = FileSystemStorage(location='media/uploads')
        saved_path = fs.save(video_file.name, video_file)
        video_path = fs.path(saved_path)

        # Define the HLS output directory
        hls_output_dir = f"media/hls/{video_file.name.split('.')[0]}"

        # Trigger the Celery task for HLS generation
        generate_hls.delay(video_path, hls_output_dir)

        return JsonResponse({
            "status": "success",
            "message": "Video uploaded and HLS generation started.",
            "hls_path": hls_output_dir
        })

    return JsonResponse({"status": "error", "message": "Invalid request or missing video file."})
