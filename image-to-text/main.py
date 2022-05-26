import base64, io, cv2
import numpy as np
from PIL import Image, ImageFilter
import tensorflow as tf
import functions_framework

@functions_framework.http
def image_to_text(request):
    im_b64 = request.json['image']
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))
    model = "semantic_model.meta"
    voc_file = "vocabulary_semantic.txt"

    tf.compat.v1.reset_default_graph()
    sess = tf.compat.v1.InteractiveSession()
    tf.compat.v1.disable_eager_execution()
    saver = tf.compat.v1.train.import_meta_graph(model)
    saver.restore(sess, model[:-5])
    graph = tf.compat.v1.get_default_graph()

    input = graph.get_tensor_by_name("model_input:0")
    seq_len = graph.get_tensor_by_name("seq_lengths:0")
    rnn_keep_prob = graph.get_tensor_by_name("keep_prob:0")
    height_tensor = graph.get_tensor_by_name("input_height:0")
    width_reduction_tensor = graph.get_tensor_by_name("width_reduction:0")
    logits = tf.compat.v1.get_collection("logits")[0]

    print(f"seq_len {seq_len}, rnn_keep_prob {rnn_keep_prob}")
    WIDTH_REDUCTION, HEIGHT = sess.run([width_reduction_tensor, height_tensor])
    decoded, _ = tf.nn.ctc_greedy_decoder(logits, seq_len)

    image_for_prediction = pre_processing(img_bytes, HEIGHT)
    seq_lenghts = [image_for_prediction.shape[2] / WIDTH_REDUCTION]
    prediction = sess.run(decoded, feed_dict={input: image_for_prediction, seq_len: seq_lenghts, rnn_keep_prob: 1.0})
    str_predictions = sparse_tensor_to_strs(prediction)
    array_of_notes = from_prediction_to_note(str_predictions, voc_file)
    if array_of_notes is not None:
        return {'array_of_notes': array_of_notes}, 200
    else:
        return "", 500


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


def sparse_tensor_to_strs(sparse_tensor):
    indices = sparse_tensor[0][0]
    values = sparse_tensor[0][1]
    dense_shape = sparse_tensor[0][2]
    strs = [[] for i in range(dense_shape[0])]
    string = []
    ptr = 0
    b = 0
    for idx in range(len(indices)):
        if indices[idx][0] != b:
            strs[b] = string
            string = []
            b = indices[idx][0]
        string.append(values[ptr])
        ptr = ptr + 1
    strs[b] = string
    return strs


def from_prediction_to_note(str_predictions, voc_file):
    array_of_notes = []
    dict_file = open(voc_file, 'r')
    dict_list = dict_file.read().splitlines()
    int2word = dict()
    cont = 0
    for word in dict_list:
        int2word[cont] = word
        cont += 1
    dict_file.close()
    for w in str_predictions[0]:
        figure = int2word[w]
        array_of_notes.append(figure)
    return array_of_notes
