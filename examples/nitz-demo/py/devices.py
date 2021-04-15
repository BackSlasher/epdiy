#!/usr/bin/env python3
from __future__ import annotations
from typing import NamedTuple, List
import math
import PIL.Image
import PIL.ImageOps

class Dimensions(NamedTuple):
    width: int
    height: int

class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Dimensions) -> Point:
        return Point(
            self.x + other.width,
            self.y + other.height,
        )

class Rectangle(NamedTuple):
    start: Point
    dimensions: Dimensions
    rotation_deg: int

    def __mul__(self, b: float) -> Rectangle:
        return Rectangle(
            start=Point(
                x=int(self.start.x * b),
                y=int(self.start.y * b),
            ),
            dimensions = Dimensions(
                width = int(self.dimensions.width * b),
                height = int(self.dimensions.height * b),
            ),
            rotation_deg = self.rotation_deg,
        )

    def get_corners(self) -> List[Point]:
        ret = []
        rotation_rad_width = math.radians(self.rotation_deg)
        # Y is upside down because top-left is 0,0
        delta_width = Dimensions(
            width=int(self.dimensions.width * math.cos(rotation_rad_width)),
            height=0 - int(self.dimensions.height * math.sin(rotation_rad_width)),
        )
        rotation_rad_height = math.radians(self.rotation_deg - 90)
        delta_height = Dimensions(
            width=int(self.dimensions.width * math.cos(rotation_rad_height)),
            height=0 - int(self.dimensions.height * math.sin(rotation_rad_height)),
        )
        # left top
        ret.append(self.start)
        # right top
        ret.append(self.start + delta_width)
        # left bottom
        ret.append(self.start + delta_height)
        # right bottom
        ret.append(self.start + delta_width + delta_height)
        return ret

    @staticmethod
    def bounding_dimensions(rectangles: Iterator[Rectangle]) -> Dimensions:
        all_points_deep = [r.get_corners() for r in rectangles]
        all_points = [item for sublist in all_points_deep for item in sublist]
        all_x = {p.x for p in all_points}
        all_y = {p.y for p in all_points}

        min_x = min(all_x)
        max_x = max(all_x)
        min_y = min(all_y)
        max_y = max(all_y)

        return Dimensions(width=max_x, height=max_y)

class Device(object):
    def __init__(self, physical_dimensions: Rectangle, address: str):
        self.phyiscal_dimensions = physical_dimensions
        self.address = address

    def get_physical_dimensions(self):
        return self.phyiscal_dimensions

    def get_address(self):
        return self.address

    def draw(self, image: PIL.Image) -> None:
        raise Exception("Not implement")

    def clear(self) -> None:
        raise Exception("Not implement")

def image_refit(image: PIL.Image, bounder: Dimensions) -> PIL.Image:
    bounder_ratio = bounder.width / bounder.height
    image_width, image_height = image.size

    image_width_by_height = int(image_height * bounder_ratio)
    image_height_by_width = int(image_width / bounder_ratio)
    if image_width > image_width_by_height:
        new_dimensions = Dimensions(image_width_by_height, image_height)
    else:
        new_dimensions = Dimensions(image_width, image_height_by_width)
    return PIL.ImageOps.fit(image, new_dimensions)

def image_crop(image: PIL.Image, rectangle: Rectangle) -> PIL.Image:
    # TODO support rotation!
    assert rectangle.rotation_deg == 0, "Dont know how to do rotations"
    return image.crop(
        (
            rectangle.start.x,
            rectangle.start.y,
            rectangle.start.x + rectangle.dimensions.width,
            rectangle.start.y + rectangle.dimensions.height,
        )
    )


class DeviceCollection(NamedTuple):
    devices: List[Device]

    def clear(self) -> None:
        [
            d.clear()
            for d in self.devices
        ]

    def bounding_dimensions(self) -> Dimensions:
        all_rectangles = [
            d.get_physical_dimensions()
            for d in self.devices
        ]
        return Rectangle.bounding_dimensions(all_rectangles)

    def draw(self, image: PIL.Image) -> None:
        # Get the overall rectangle
        bounder = self.bounding_dimensions()
        # Fit the image to match the bounder
        image = image_refit(image, bounder)
        # calculate the pixel to cm ratio
        pixel_in_cm = image.size[0] / bounder.width

        devices_and_images = [
            (device, image_crop(image, device.get_physical_dimensions() * pixel_in_cm))
            for device in self.devices
        ]

        for device,cropped_image in devices_and_images:
            device.draw(cropped_image)
