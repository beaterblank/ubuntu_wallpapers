import os

from PIL import Image
from dataclasses import dataclass
from abc import ABC, abstractmethod

from util import PathLike,List

class FitType(ABC):
    def __init__(self, width:float, height:float, image_dir:PathLike):
        """
        Initialize the FitType with target width, height, and an image.

        Args:
            width (int): The target width for the image.
            height (int): The target height for the image.
            image_dir (str): The path to the image file.
        """
        self.width = width
        self.height = height
        self.image = Image.open(image_dir)

    @abstractmethod
    def fit_to_size(self):
        """
        Abstract method to fit the image to the specified size.

        Returns:
            Image.Image: The processed image.
        """
        pass

class Fill(FitType):
    def fit_to_size(self):
        """
        Resize the image to fit the specified size by filling and cropping.

        Returns:
            Image.Image: The processed image.
        """
        image = self.image
        image_ratio = image.width / image.height
        target_ratio = self.width / self.height

        if image_ratio > target_ratio:
            new_height = self.height
            new_width = int(new_height * image_ratio)
        else:
            new_width = self.width
            new_height = int(new_width / image_ratio)

        image = image.resize((new_width, new_height), Image.LANCZOS)
        x_crop = (new_width - self.width) // 2
        y_crop = (new_height - self.height) // 2
        return image.crop((x_crop, y_crop, x_crop + self.width, y_crop + self.height))

class Fit(FitType):
    def fit_to_size(self):
        """
        Resize the image to fit within the specified size while maintaining aspect ratio,
        and place it on a black background.

        Returns:
            Image.Image: The processed image.
        """
        image = self.image
        image.thumbnail((self.width, self.height), Image.LANCZOS)
        background = Image.new('RGB', (self.width, self.height), (0, 0, 0))  # Black background
        x_offset = 0
        y_offset = 0
        background.paste(image, (x_offset, y_offset))
        return background

class Stretch(FitType):
    def fit_to_size(self):
        """
        Resize the image to exactly fit the specified size.

        Returns:
            Image.Image: The processed image.
        """
        image = self.image
        return image.resize((self.width, self.height), Image.LANCZOS)

class Tile(FitType):
    def fit_to_size(self):
        """
        Tile the image to cover the specified size.

        Returns:
            Image.Image: The processed image.
        """
        image = self.image
        tile_width, tile_height = image.size
        background = Image.new('RGB', (self.width, self.height))
        for x in range(0, self.width, tile_width):
            for y in range(0, self.height, tile_height):
                background.paste(image, (x, y))
        return background

class Center(FitType):
    def fit_to_size(self):
        """
        Center the image on a black background of the specified size.

        Returns:
            Image.Image: The processed image.
        """
        image = self.image
        background = Image.new('RGB', (self.width, self.height), (0, 0, 0))  # Black background
        x_offset = (self.width - image.width) // 2
        y_offset = (self.height - image.height) // 2
        background.paste(image, (x_offset, y_offset))
        return background

from enum import Enum
class FIT(Enum):
    FILL = Fill
    FIT = Fit
    CENTER = Center
    STRETCH = Stretch
    TILE = Tile

@dataclass
class Wallpaper:
    image_dir:PathLike
    # monitor details
    x:float
    y:float
    w:float
    h:float
    device_name:str
    fit_type:FitType

def make_wallpaper(wallpapers:List[Wallpaper],bg_w,bg_h,name="default")->PathLike:
    background = Image.new('RGB', (bg_w, bg_h), (0, 0, 0))
    for w in wallpapers:
        fitter = w.fit_type(w.w,w.h,w.image_dir)
        image = fitter.fit_to_size()
        background.paste(image,(w.x,w.y))
    save_dir = f"./temp/background_{name}.jpg"
    os.makedirs("./temp/",exist_ok=True)
    background.save(save_dir)
    return save_dir

def test_fits():
    image_path = './test_images/test.jpg'
    output_dir = './test_images/'

    # Fill example
    fill_processor = Fill(width=3000, height=2000, image_dir=image_path)
    fill_image = fill_processor.fit_to_size()
    fill_image.save(f'{output_dir}processed_fill.jpg')

    # Fit example
    fit_processor = Fit(width=3000, height=2000, image_dir=image_path)
    fit_image = fit_processor.fit_to_size()
    fit_image.save(f'{output_dir}processed_fit.jpg')

    # Stretch example
    stretch_processor = Stretch(width=3000, height=2000, image_dir=image_path)
    stretch_image = stretch_processor.fit_to_size()
    stretch_image.save(f'{output_dir}processed_stretch.jpg')

    # Tile example
    tile_processor = Tile(width=3000, height=2000, image_dir=image_path)
    tile_image = tile_processor.fit_to_size()
    tile_image.save(f'{output_dir}processed_tile.jpg')

    # Center example
    center_processor = Center(width=3000, height=2000, image_dir=image_path)
    center_image = center_processor.fit_to_size()
    center_image.save(f'{output_dir}processed_center.jpg')

if __name__=="__main__":
    test_fits()
