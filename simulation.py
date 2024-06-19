import pygame as pg

from pygame import Vector2
from settings import *

from font import Font

from builder import Builder
from ridged_body import RidgedBody

class Simulation:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pg.NOFRAME, vsync=VSYNC)
        self.clock = pg.time.Clock()

        self.close_program = False
        self.paused = False
        self.debug = False
    
        self.title_font = Font(self.screen, TITLE_SIZE)
        self.text_font = Font(self.screen, TEXT_SIZE)

        self.builder = Builder()

        self.selected : RidgedBody = None
        self.grab_offset = Vector2(0, 0)


    def run(self):
        while not self.close_program:
            self.event_manager()
            self.update()
            self.render()


    def event_manager(self):
        # event check
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close_program = True
            
            elif event.type == pg.KEYDOWN:
                self.handle_key_press(event)
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.handle_mouse_press(event)
            
            elif event.type == pg.MOUSEBUTTONUP:
                self.handle_mouse_release(event)
    
    
    def handle_mouse_press(self, event):
        pressed = pg.mouse.get_pressed()
        position = pg.mouse.get_pos()

        # manipulate existing ridged bodies
        if self.debug:
            self.selected = self.builder.get_pressed(position)
            self.grab_offset = Vector2(position) - self.selected.get_center()
        
        # create a ridged body
        else:
            self.builder.create_physics_rect(position)
        

    def handle_mouse_release(self, event):
        if self.selected != None:
            self.selected = None
        
        else:
            self.builder.check_mouse_release()



    def handle_key_press(self, event):
        if event.key == pg.K_ESCAPE:
            self.close_program = True
        
        elif event.key == pg.K_SPACE:
            self.paused = not self.paused
        
        elif event.key == pg.K_d:
            self.debug = not self.debug
        


    def update(self):
        self.clock.tick(FRAME_RATE)

        self.builder.update(self.clock.get_time() / 1000.0)

        if self.selected != None:
            self.selected.set_center(Vector2(pg.mouse.get_pos()) - self.grab_offset)

        self.event_manager()
    

    def render(self):
        self.screen.fill(SCREEN_COLOR)

        self.builder.render(self.screen, self.debug)

        if self.selected != None:
            self.selected.render(self.screen, True, True)

        self.render_screen_stats()

        pg.display.update()
    

    def render_screen_stats(self):
        start_pos = (40, 60)
        y_spacing = 16
        col = (255, 255, 255)

        def draw(txt, idx):
            self.text_font.draw(txt, (start_pos[0], start_pos[1] + y_spacing * idx), col)

        self.title_font.draw(TITLE, (40, 40), (255, 255, 255))
        draw(f"{round(self.clock.get_fps())}fps", 0)
        draw("pause [space]", 2)
        draw("escape [ESC]", 3)
        draw("debug [D]", 4)
        draw("bounding box [right press + drag]", 5)
        draw("physics box [left press + drag]", 6)
