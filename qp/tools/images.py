import os
import secrets

from PIL import Image


def get_square(image):
    """Cropping image to square"""
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


def remove_transparency(image, bg_color=(255, 255, 255)):
    """Removing alpha channel"""
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        alpha = image.getchannel("A")

        bg = Image.new("RGBA", image.size, bg_color + (255,))
        bg.paste(image, mask=alpha)
        return bg
    else:
        return image


def save_image(image_data, folder="avatars", size=(150, 150), ext="png", bg_color=(255, 255, 255), remove=None):
    """Saving image"""
    images_folder = "qp/static/" + folder
    image_filename = secrets.token_hex(16)
    image_path = images_folder + "/" + image_filename + "." + ext

    image = Image.open(image_data)
    image = get_square(image)
    image.thumbnail(size)
    if bg_color:
        image = remove_transparency(image, bg_color)
    image.save(image_path, ext)

    if type(remove) is str and remove + "." + ext in os.listdir(images_folder):
        os.remove(images_folder + "/" + remove + "." + ext)

    return image_filename
