import secrets
from PIL import Image


def get_square(image):
    width, height = image.size
    crop = [0, 0, width, height]
    if width > height:
        delta = (width - height) // 2
        crop[0] += delta
        crop[2] -= delta
    if height > width:
        delta = (height - width) // 2
        crop[1] += delta
        crop[3] -= delta
    return image.crop(crop)


def save_image(image_data, folder="/avatars", size=(150, 150), ext="png"):
    image_filename = secrets.token_hex(16)
    image_path = "static" + folder + "/" + image_filename + "." + ext

    image = Image.open(image_data)
    image = get_square(image)
    image.thumbnail(size)
    image.save(image_path, ext)

    return image_filename
