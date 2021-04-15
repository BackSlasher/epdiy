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
            width=int(self.width * math.cos(rotation_rad_height)),
            height=0 - int(self.height * math.sin(rotation_rad_height)),
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
    def bounding_rectangle(rectangles: Iterator[Rectangle]) -> Rectangle:
        all_points_deep = [r.get_corners() for r in rectangles]
        all_points = [item for sublist in all_points_deep for item in sublist]
        all_x = {p.x for p in all_points}
        all_y = {p.y for p in all_points}

        min_x = min(x)
        max_x = max(x)
        min_y = min(y)
        max_y = max(y)

        return Rectangle(
                start=Point(min_x, min_y),
                dimensions=Dimensions(width=max_x, height=max_y)
        )

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

class DeviceCollection(NamedTuple):
    devices: List[Device]

    def clear(self) -> None:
        [
            d.clear()
            for d in self.devices
        ]

    def draw(self, image: PIL.Image) -> None:
        # TODO smarter
        # img = PIL.ImageOps.fit(img, size)
        [
            d.draw(image)
            for d in self.devices
        ]
