import datetime
import os
from io import BytesIO
import base64

from PIL import Image, ImageDraw, ImageOps, ImageFont


def get_size():
    size = 5
    return size


def get_body_image(context, width, height):
    body_image_base64 = context['body_base64']
    if body_image_base64:
        body_image_base64_bytes = base64.b64decode(body_image_base64)
        body_image = Image.open(BytesIO(body_image_base64_bytes))
    else:
        raise Exception('Não é possível gerar o layout, pois não há uma imagem para o corpo do layout.')
    body_image_adjusted = body_image_adjust(body_image, width, height)
    return body_image_adjusted


def body_image_adjust(body_image, width, height):
    body_image_width, body_image_height = body_image.size
    body_image_ratio = body_image_width / body_image_height
    if body_image_ratio >= 1:
        body_image_width_new = width * get_size()
        body_image_height_new = round(body_image_width_new * (1 / body_image_ratio))
        body_image_height_new_real_size = body_image_height_new / get_size() 
        if body_image_height_new_real_size > height:
            taxa_de_reducao = height/body_image_height_new_real_size-1
            body_image_width_new = round(body_image_width_new * (1 + taxa_de_reducao))
            body_image_height_new = round(body_image_height_new * (1 + taxa_de_reducao))
    else:
        body_image_height_new = height * get_size()
        body_image_width_new = round(body_image_height_new * body_image_ratio)
    size = (body_image_width_new, body_image_height_new)
    return body_image.resize(size, Image.ANTIALIAS)


def write_text_center(image, coordinate, text, font, fill, font_size):
    font_size = int(font_size / 3 * get_size())
    draw = ImageDraw.Draw(image)
    font = get_font(font, font_size)
    text_width, text_height = draw.textsize(text, font=font)
    rectangle_width = coordinate['width']
    width_mid = (rectangle_width * get_size() - text_width) / 2
    rectangle_height = coordinate['height']
    height_mid = (rectangle_height * get_size() - text_height) / 2    
    x = (coordinate['offset_left'] + coordinate['left']) * get_size() + width_mid
    y = (coordinate['offset_top'] + coordinate['top']) * get_size() + height_mid
    xy = (x, y)
    draw.text(xy, text, align='center', font=font, fill=fill)


def write_text_left(image, coordinate, text, font, fill, font_size):
    font_size = int(font_size / 3 * get_size())
    draw = ImageDraw.Draw(image)
    font = get_font(font, font_size)
    text_width, text_height = draw.textsize(text, font=font)
    rectangle_width = coordinate['width']
    width_mid = (rectangle_width * get_size() - text_width) / 2
    rectangle_height = coordinate['height']
    height_mid = (rectangle_height * get_size() - text_height) / 2    
    x = (coordinate['offset_left'] + coordinate['left']) * get_size() + 5
    y = (coordinate['offset_top'] + coordinate['top']) * get_size() + height_mid
    xy = (x, y)
    draw.text(xy, text, align='left', font=font, fill=fill)


def write_text_left_top(image, coordinate, text, font, fill, font_size):
    font_size = int(font_size / 3 * get_size())
    draw = ImageDraw.Draw(image)
    font = get_font(font, font_size)
    x = (coordinate['offset_left'] + coordinate['left']) * get_size()
    y = (coordinate['offset_top'] + coordinate['top']) * get_size()
    xy = (x, y)
    draw.text(xy, text, align='left', font=font, fill=fill)


def break_fix(text, width, font, draw):
    if not text:
        return
    lo = 0
    hi = len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        t = text[:mid]
        w, h = draw.textsize(t, font=font)
        if w <= width:
            lo = mid
        else:
            hi = mid - 1
    t = text[:lo]
    w, h = draw.textsize(t, font=font)
    yield t, w, h
    yield from break_fix(text[lo:], width, font, draw)


def fit_text(img, coordinate, text, font, color):
    
    width = img.size[0] - 2
    
    draw = ImageDraw.Draw(img)
    
    pieces = list(break_fix(text, width, font, draw))

    height = sum(p[2] for p in pieces)
    
    if height > img.size[1]:
        raise ValueError("text doesn't fit")
    y = (img.size[1] - height) // 2

    for t, w, h in pieces:
        x = (img.size[0] - w) // 2
        draw.text((x, y), t, align='left', font=font, fill=color)
        y += h


def convert_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format='PNG')
    image_base64_string = base64.b64encode(buffered.getvalue()).decode()
    image_base64_string = 'data:image/png;base64,' + image_base64_string
    return image_base64_string


def get_logo_image(width):
    width = width * get_size()
    logo_address = get_contents_folder() + r'/logo.png'
    logo_image = Image.open(logo_address)
    logo_width, logo_height = logo_image.size
    logo_ratio = logo_width / logo_height
    logo_width_new = width
    logo_height_new = round(logo_width_new / logo_ratio)
    new_size = (logo_width_new, logo_height_new)
    logo_image = logo_image.resize(new_size, Image.ANTIALIAS)
    return logo_image


def add_border_to_image(image, border, color):
    # top, right, bottom, left
    border = (border, border, border, border)
    return ImageOps.expand(image, border=border, fill=color)


def resize_image(image, width):
    width_, height_ = image.size
    ratio = width_ / height_
    width_new = width
    height_new = round(width_new / ratio)
    new_size = (width_new, height_new)
    image = image.resize(new_size, Image.ANTIALIAS)
    return image


def get_center_middle_image_box(image, coordinate):

    # coordinate
    width = coordinate['width']
    height = coordinate['height']
    top = coordinate['top']
    left = coordinate['left']
    offset_left = coordinate['offset_left']
    offset_top = coordinate['offset_top']

    # height / width
    image_width, image_height = image.size
    image_width = image_width / get_size()
    image_height = image_height / get_size()
    
    # center / middle
    image_margin_center = (width - image_width) / 2
    image_margin_middle = (height - image_height) / 2
    
    # box
    box_left = round(image_margin_center + offset_left + left) * get_size()
    box_top = round(image_margin_middle + offset_top + top) * get_size()
    box = (box_left, box_top)

    return box


def get_contents_folder():
    logo_local = get_folder(r'draw/contents')
    return  logo_local


def get_image_name():
    now_format = '%Y_%m_%d_%H%M%S_%f'
    now = datetime.datetime.now()
    now_string = now.strftime(now_format)
    layout_file_name = '{}_{}'.format('layout', now_string)
    return layout_file_name


def get_folder(path):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(base, path)
    return folder


def get_font(font_name, size):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_file_location_address = os.path.join(base, 'draw/contents/fonts')
    font_file_address = os.path.join(font_file_location_address, font_name)
    font_file = open(font_file_address, 'rb')
    font_file_bytes = BytesIO(font_file.read())
    return ImageFont.truetype(font_file_bytes, size)


def write_draw_rectangle(image, coordinate):
    
    # margin
    margin_left = coordinate['left']
    margin_top = coordinate['top']

    # offsets
    offset_top = coordinate['offset_top'] + margin_top
    offset_left = coordinate['offset_left'] + margin_left

    # width / height
    width = coordinate['width']
    height = coordinate['height']

    # somes calcs
    width = width + offset_left
    height = height + offset_top
    top = offset_top
    left = offset_left

    # style
    fill = '#fff'
    outline = '#000'
    stroke = 1

    draw_rectangle(image, width, height, top, left, fill, outline, stroke)


def write_draw_rectangle_style(image, coordinate, style):
    
    # margin
    margin_left = coordinate['left']
    margin_top = coordinate['top']

    # offsets
    offset_top = coordinate['offset_top'] + margin_top
    offset_left = coordinate['offset_left'] + margin_left

    # width / height
    width = coordinate['width']
    height = coordinate['height']

    # somes calcs
    width = width + offset_left
    height = height + offset_top
    top = offset_top
    left = offset_left

    # style
    fill = style['fill']
    outline = style['outline']
    stroke = style['stroke']
    draw_rectangle(image, width, height, top, left, fill, outline, stroke)


def draw_rectangle(image, width, height, top, left, fill, outline, stroke):
    coordinate = get_coordinate(width, height, left, top)
    draw = ImageDraw.Draw(image)
    draw.rectangle(coordinate, fill=fill, outline=outline, width=stroke)


def get_coordinate(width, height, left, top):

    # width & height
    width = width * get_size()
    height = height * get_size()  

    # margin
    left = left * get_size()
    top = top * get_size()

    # x
    xa = width
    xb = top
    x = (xa, xb)

    # y
    ya = left
    yb = height
    y = (ya, yb)

    # xy
    xy = [x, y]

    return xy


def add_margin(image):
    right = 35
    left = 35
    top = 35
    bottom = 35
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(image.mode, (new_width, new_height), (255, 255, 255))
    result.paste(image, (left, top))
    return result