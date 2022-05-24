import functions_framework

CLOUD = False

@functions_framework.http
def image_to_text(request):
    request_body = request.json
    bpm = request_body["bpm"]
    image_b64 = request_body["image"]
    return "Hello World!", 200