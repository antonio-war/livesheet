import base64, io, cv2
import numpy as np
from PIL import Image, ImageFilter 
import functions_framework

@functions_framework.http
def hello(request):
    im_b64 = request.json['image']
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))
    img_for_prediction = pre_processing(img_bytes, HEIGHT)
    
    return {'greeting' : "Ciao TOTORE"}

def pre_processing(file, height):
    image = Image.open(io.BytesIO(file)).convert('L')
    image = image.filter(ImageFilter.SHARPEN)
    image = np.array(image)
    image = resize(image, height)
    image = normalize(image)

    image = np.asarray(image).reshape(1, image.shape[0], image.shape[1], 1)
    return image

def normalize(image):
    return (255. - image) / 255.


def resize(image, height):
    width = int(float(height * image.shape[1]) / image.shape[0])
    sample_img = cv2.resize(image, (width, height))
    return sample_img
