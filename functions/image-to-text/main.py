import functions_framework

CLOUD = False

@functions_framework.http
def image_to_text(request):
    request_body = request.json
    bpm = request_body["bpm"]
    image_b64 = request_body["image"]
    image = rebuild_image(image_b64)
    return "Hello World!", 200

def rebuild_image(image_b64):
    return