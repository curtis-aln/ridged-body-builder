import pygame as pg

from pygame import Vector2, Rect
from ridged_body import RidgedBody, ridged_body_from_rect
from settings import *

# an instance of this is created when the user is making a rect
class CreateRect:
    def __init__(self, start_position, color) -> None:
        self.start_position = start_position
        self.color = color
        
    def get_rect(self):
        pos_start = Vector2(self.start_position)
        pos_end = Vector2(pg.mouse.get_pos())

        size = pos_end - pos_start

        # Determine the correct position and size for the rectangle
        rect_x = pos_start.x
        rect_y = pos_start.y
        rect_width = size.x
        rect_height = size.y

        if size.x < 0:
            rect_x = pos_end.x
            rect_width = -size.x

        if size.y < 0:
            rect_y = pos_end.y
            rect_height = -size.y

        return Rect(rect_x, rect_y, rect_width, rect_height)


    def render(self, window):
        pg.draw.rect(window, self.color, self.get_rect(), RECT_WIDTH)
            


class Builder:
    def __init__(self) -> None:
        self.objects : list[RidgedBody] = []

        # when the mouse is pressed down this is set to True
        self.creating = False
        self.rect_builder = CreateRect((0, 0), (255, 255, 255))
    

    def create_physics_rect(self, position):
        self.rect_builder.start_position = position
        self.creating = True
    

    def check_mouse_release(self):
        if self.creating == True:
            self.creating = False

            rect = self.rect_builder.get_rect()
            if rect.w == 0 or rect.h == 0:
                return
    
            self.objects.append(ridged_body_from_rect(rect))
        

    def get_pressed(self, position) -> bool:
        # checks if the mouse is hovering over any of the ridget objects
        for body in self.objects:
            if body.contains_point(position):
                return body
        
        return None
    

    def update(self, dt : float) -> None:
        for body in self.objects:
            body.update(dt)

    
    def render(self, window : pg.Surface, debug : bool = False) -> None:
        if self.creating:
            self.rect_builder.render(window)
        
        for rect in self.objects:
            rect.render(window, debug)
        
    
