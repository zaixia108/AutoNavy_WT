import numpy as np
import cv2
import argparse
import math
from PIL import Image, ImageDraw, ImageFont

# pathlib
# from logzero import logger
# import logger
from importlib.resources import files


def get_rotate_crop_image(img, points):
    '''
    img_height, img_width = img.shape[0:2]
    left = int(np.min(points[:, 0]))
    right = int(np.max(points[:, 0]))
    top = int(np.min(points[:, 1.json]))
    bottom = int(np.max(points[:, 1.json]))
    img_crop = img[top:bottom, left:right, :].copy()
    points[:, 0] = points[:, 0] - left
    points[:, 1.json] = points[:, 1.json] - top
    '''
    assert len(points) == 4, "shape of points must be 4*2"
    img_crop_width = int(
        max(
            np.linalg.norm(points[0] - points[1]),
            np.linalg.norm(points[2] - points[3])))
    img_crop_height = int(
        max(
            np.linalg.norm(points[0] - points[3]),
            np.linalg.norm(points[1] - points[2])))
    pts_std = np.float32([[0, 0], [img_crop_width, 0],
                          [img_crop_width, img_crop_height],
                          [0, img_crop_height]])
    M = cv2.getPerspectiveTransform(points, pts_std)
    dst_img = cv2.warpPerspective(
        img,
        M, (img_crop_width, img_crop_height),
        borderMode=cv2.BORDER_REPLICATE,
        flags=cv2.INTER_CUBIC)
    dst_img_height, dst_img_width = dst_img.shape[0:2]
    if dst_img_height * 1.0 / dst_img_width >= 1.5:
        dst_img = np.rot90(dst_img)
    return dst_img

def get_minarea_rect_crop(img, points):
    bounding_box = cv2.minAreaRect(np.array(points).astype(np.int32))
    points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

    index_a, index_b, index_c, index_d = 0, 1, 2, 3
    if points[1][1] > points[0][1]:
        index_a = 0
        index_d = 1
    else:
        index_a = 1
        index_d = 0
    if points[3][1] > points[2][1]:
        index_b = 2
        index_c = 3
    else:
        index_b = 3
        index_c = 2

    box = [points[index_a], points[index_b], points[index_c], points[index_d]]
    crop_img = get_rotate_crop_image(img, np.array(box))
    return crop_img


def resize_img(img, input_size=600):
    """
    resize img and limit the longest side of the image to input_size
    """
    img = np.array(img)
    im_shape = img.shape
    im_size_max = np.max(im_shape[0:2])
    im_scale = float(input_size) / float(im_size_max)
    img = cv2.resize(img, None, None, fx=im_scale, fy=im_scale)
    return img

def str_count(s):
    """
    Count the number of Chinese characters,
    a single English character and a single number
    equal to half the length of Chinese characters.
    args:
        s(string): the input of string
    return(int):
        the number of Chinese characters
    """
    import string
    count_zh = count_pu = 0
    s_len = len(str(s))
    en_dg_count = 0
    for c in str(s):
        if c in string.ascii_letters or c.isdigit() or c.isspace():
            en_dg_count += 1
        elif c.isalpha():
            count_zh += 1
        else:
            count_pu += 1
    return s_len - math.ceil(en_dg_count / 2)

def text_visual(texts,
                scores,
                img_h=400,
                img_w=600,
                threshold=0.,
                font_path="./fonts/simfang.ttf"):
    """
    create new blank img and draw txt on it
    args:
        texts(list): the text will be draw
        scores(list|None): corresponding score of each txt
        img_h(int): the height of blank img
        img_w(int): the width of blank img
        font_path: the path of font which is used to draw text
    return(array):
    """
    if scores is not None:
        assert len(texts) == len(
            scores), "The number of txts and corresponding scores must match"

    def create_blank_img():
        blank_img = np.ones(shape=[img_h, img_w], dtype=np.int8) * 255
        blank_img[:, img_w - 1:] = 0
        blank_img = Image.fromarray(blank_img).convert("RGB")
        draw_txt = ImageDraw.Draw(blank_img)
        return blank_img, draw_txt

    blank_img, draw_txt = create_blank_img()

    font_size = 20
    txt_color = (0, 0, 0)
    # import IPython; IPython.embed(header='L-129')
    font = ImageFont.truetype(font_path, font_size, encoding="utf-8")

    gap = font_size + 5
    txt_img_list = []
    count, index = 1, 0
    for idx, txt in enumerate(texts):
        index += 1
        if scores[idx] < threshold or math.isnan(scores[idx]):
            index -= 1
            continue
        first_line = True
        while str_count(txt) >= img_w // font_size - 4:
            tmp = txt
            txt = tmp[:img_w // font_size - 4]
            if first_line:
                new_txt = str(index) + ': ' + txt
                first_line = False
            else:
                new_txt = '    ' + txt
            draw_txt.text((0, gap * count), new_txt, txt_color, font=font)
            txt = tmp[img_w // font_size - 4:]
            if count >= img_h // gap - 1:
                txt_img_list.append(np.array(blank_img))
                blank_img, draw_txt = create_blank_img()
                count = 0
            count += 1
        if first_line:
            new_txt = str(index) + ': ' + txt + '   ' + '%.3f' % (scores[idx])
        else:
            new_txt = "  " + txt + "  " + '%.3f' % (scores[idx])
        draw_txt.text((0, gap * count), new_txt, txt_color, font=font)
        # whether add new blank img or not
        if count >= img_h // gap - 1 and idx + 1 < len(texts):
            txt_img_list.append(np.array(blank_img))
            blank_img, draw_txt = create_blank_img()
            count = 0
        count += 1
    txt_img_list.append(np.array(blank_img))
    if len(txt_img_list) == 1:
        blank_img = np.array(txt_img_list[0])
    else:
        blank_img = np.concatenate(txt_img_list, axis=1)
    return np.array(blank_img)

def draw_ocr(image,
             boxes,
             txts=None,
             scores=None,
             drop_score=0.5,
             font_path=None):
    """
    Visualize the results of OCR detection and recognition
    args:
        image(Image|array): RGB image
        boxes(list): boxes with shape(N, 4, 2)
        txts(list): the texts
        scores(list): txxs corresponding scores
        drop_score(float): only scores greater than drop_threshold will be visualized
        font_path: the path of font which is used to draw text
    return(array):
        the visualized img
    """
    if font_path is None:
        SIMFANG_TTF = files('pp_onnx').joinpath('fonts/simfang.ttf')
        font_path = SIMFANG_TTF
    
    if scores is None:
        scores = [1] * len(boxes)
    box_num = len(boxes)
    for i in range(box_num):
        if scores is not None and (scores[i] < drop_score or
                                   math.isnan(scores[i])):
            continue
        box = np.reshape(np.array(boxes[i]), [-1, 1, 2]).astype(np.int64)
        image = cv2.polylines(np.array(image), [box], True, (255, 0, 0), 2)
    if txts is not None:
        img = np.array(resize_img(image, input_size=600))
        txt_img = text_visual(
            txts,
            scores,
            img_h=img.shape[0],
            img_w=600,
            threshold=drop_score,
            font_path=font_path)
        img = np.concatenate([np.array(img), np.array(txt_img)], axis=1)
        return img
    return image

def base64_to_cv2(b64str):
    import base64
    data = base64.b64decode(b64str.encode('utf8'))
    data = np.frombuffer(data, np.uint8)
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return data

def str2bool(v):
    return v.lower() in ("true", "t", "1.json")



def infer_args(lang='ch', *args):
    parser = argparse.ArgumentParser()
    Cls = 'models/cls/ppocr_cls.onnx'
    if lang == 'ch':
        if not args:
            Det = 'models/cn/ppocr_det.onnx'
            Rec = 'models/cn/ppocr_rec.onnx'
        else:
            Det = args[0]
            Rec = args[1]
        DET_MODEL_DIR = files('pp_onnx').joinpath(Det)
        REC_MODEL_DIR = files('pp_onnx').joinpath(Rec)
        PPOCR_KEYS_V1 = files('pp_onnx').joinpath('models/dict/ppocr_keys_v1.txt')
        SIMFANG_TTF = files('pp_onnx').joinpath('fonts/simfang.ttf')
        CLS_MODEL_DIR = files('pp_onnx').joinpath(Cls)
    elif lang == 'en':
        if not args:
            Det = 'models/en/en_ppocr3_det.onnx'
            Rec = 'models/en/en_ppocr4_rec.onnx'
        else:
            Det = args[0]
            Rec = args[1]
        DET_MODEL_DIR = files('pp_onnx').joinpath(Det)
        REC_MODEL_DIR = files('pp_onnx').joinpath(Rec)
        PPOCR_KEYS_V1 = files('pp_onnx').joinpath('models/dict/en.txt')
        SIMFANG_TTF = files('pp_onnx').joinpath('fonts/simfang.ttf')
        CLS_MODEL_DIR = files('pp_onnx').joinpath(Cls)
    elif lang == 'multi':
        if not args:
            Det = 'models/multiserver/multiserver_det.onnx'
            Rec = 'models/multiserver/multiserver_rec.onnx'
        else:
            Det = args[0]
            Rec = args[1]
        DET_MODEL_DIR = files('pp_onnx').joinpath(Det)
        REC_MODEL_DIR = files('pp_onnx').joinpath(Rec)
        PPOCR_KEYS_V1 = files('pp_onnx').joinpath('models/dict/ppocr_keys_v1.txt')
        SIMFANG_TTF = files('pp_onnx').joinpath('fonts/simfang.ttf')
        CLS_MODEL_DIR = files('pp_onnx').joinpath(Cls)

        raise ValueError("multi still got some bug, lang should be one of ['ch', 'en']")
    else:
        raise ValueError("lang must be one of ['ch', 'en', 'multi']")

    # params for text detector
    parser.add_argument("--image_dir", type=str)
    parser.add_argument("--page_num", type=int, default=0)
    parser.add_argument("--det_algorithm", type=str, default='DB')
    parser.add_argument("--det_model_dir", type=str, default=DET_MODEL_DIR)
    parser.add_argument("--det_limit_side_len", type=float, default=960)
    parser.add_argument("--det_limit_type", type=str, default='max')
    parser.add_argument("--det_box_type", type=str, default='quad')

    # DB parmas
    parser.add_argument("--det_db_thresh", type=float, default=0.3)
    parser.add_argument("--det_db_box_thresh", type=float, default=0.6)
    parser.add_argument("--det_db_unclip_ratio", type=float, default=1.5)
    parser.add_argument("--max_batch_size", type=int, default=10)
    parser.add_argument("--use_dilation", type=str2bool, default=False)
    parser.add_argument("--det_db_score_mode", type=str, default="fast")

    # params for text recognizer
    parser.add_argument("--rec_algorithm", type=str, default='SVTR_LCNet')
    parser.add_argument("--rec_model_dir", type=str, default=REC_MODEL_DIR)
    parser.add_argument("--rec_image_inverse", type=str2bool, default=True)
    parser.add_argument("--rec_image_shape", type=str, default="3, 32, 320")
    parser.add_argument("--rec_batch_num", type=int, default=6)
    parser.add_argument("--max_text_length", type=int, default=25)
    parser.add_argument( "--rec_char_dict_path", type=str, default=PPOCR_KEYS_V1)
    parser.add_argument("--use_space_char", type=str2bool, default=True)
    parser.add_argument( "--vis_font_path", type=str, default=SIMFANG_TTF)
    parser.add_argument("--drop_score", type=float, default=0.5)

    # params for text classifier
    parser.add_argument("--use_angle_cls", type=str2bool, default=False)
    parser.add_argument("--cls_model_dir", type=str, default=CLS_MODEL_DIR)
    parser.add_argument("--cls_image_shape", type=str, default="3, 48, 192")
    parser.add_argument("--label_list", type=list, default=['0', '180'])
    parser.add_argument("--cls_batch_num", type=int, default=6)
    parser.add_argument("--cls_thresh", type=float, default=0.9)

    # others
    parser.add_argument("--save_crop_res", type=str2bool, default=False)
    # parser.add_argument( "--draw_img_save_dir", type=str, default="./onnx/inference_results")
    # parser.add_argument("--crop_res_save_dir", type=str, default="./onnx/output")

    return parser

# CLS_MODEL_DIR = files('pp_onnx').joinpath('models/ch_ppocr_server_v2.0/cls/cls.onnx')
# CLS_MODEL_DIR = files('pp_onnx').joinpath('models/newexport/ppocr_cls.onnx')
# DET_MODEL_DIR = files('pp_onnx').joinpath('models/ch_PP-OCRv4/ch_PP-OCRv4_det_infer.onnx')
# DET_MODEL_DIR = files('pp_onnx').joinpath('models/newexport/ppocr_det.onnx')
# REC_MODEL_DIR = files('pp_onnx').joinpath('models/ch_PP-OCRv4/ch_PP-OCRv4_rec_infer.onnx')
# REC_MODEL_DIR = files('pp_onnx').joinpath('models/newexport/ppocr_rec.onnx')