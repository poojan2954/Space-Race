import random
from kivy.properties import ObjectProperty
from kivy.config import Config
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '400')
from kivy.properties import StringProperty
from kivy.graphics import Triangle
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Quad
from kivy import platform
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import NumericProperty
from kivy.properties import Clock


Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transform_fun import transform,transform_2D,transform_perspective
    from action import _on_keyboard_down , _on_keyboard_up , on_touch_down , on_touch_up , keyboard_closed
    
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    V_NB_LINES = 8
    V_LINES_SPACING = .4  # % in screen(Width)
    vertical_lines = []
    
    H_NB_LINES = 15
    H_LINES_SPACING = 0.19  # % in screen(Height)
    horizontal_lines = []
    
    SPEED = 1.2
    current_y_loop = 0
    current_offset_y = 0
    
    SPEED_X = 1.8
    current_speed_x = 0
    current_offset_x = 0
    
    NB_TILES = 16
    tiles = []
    tiles_coordinates = []
    
    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [ (0 , 0) , (0 , 0) , (0 , 0) ]
    
    state_game_over = False
    state_game_started = False
    
    menu_title = StringProperty("  S  P  A  C  E    R  A  C  E  ")
    menu_button_title = StringProperty("START")
    score_txt = StringProperty()
    
    
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()
        
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down = self._on_keyboard_down)
            self._keyboard.bind(on_key_up = self._on_keyboard_up)
            
        
        Clock.schedule_interval(self.update ,1.0 / 60.0)
    
    def reset_game(self):
        self.current_y_loop = 0
        self.current_offset_y = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
    
        self.tiles_coordinates = []
        self.score_txt = "SCORE: " + str(self.current_y_loop)
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    
        
    def is_desktop (self):
        if platform in ('linux','win','macosx'):
            return True
        return False
        
    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()
            
    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        self.ship_coordinates [0] = (center_x-ship_half_width,base_y)
        self.ship_coordinates [1] = (center_x , base_y + ship_height)
        self.ship_coordinates [2] = (center_x + ship_half_width,base_y) 
        
        
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        
        
        self.ship.points = [x1,y1,x2,y2,x3,y3]
        
    def check_ship_collision(self):
        for i in range (0,len(self.tiles_coordinates)):
            tile_x , tile_y = self.tiles_coordinates[i]
            if tile_y > self.current_y_loop + 1:
                return False
            if self.check_ship_tile_collision(tile_x,tile_y):
                return True
        return False
        
    def check_ship_tile_collision(self,tile_x,tile_y):
        xmin,ymin = self.get_tile_coordinates(tile_x,tile_y)
        xmax,ymax = self.get_tile_coordinates(tile_x+1,tile_y+1)
        for i in range(0,3):
            px,py = self.ship_coordinates[i]
            if xmin<= px <= xmax and ymin<=py <= ymax:
                return True        
        return False
    def init_tiles(self):
        # Initialize vertical lines with the canvas and color
        with self.canvas:
            Color(1, 1, 1)  # Set white color for the lines
            for i in range(0,self.NB_TILES):
                self.tiles.append(Quad())
    
    def pre_fill_tiles_coordinates(self):
        for i in range(0,10):
            self.tiles_coordinates.append((0 , i))
            
    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        
        # if self.tiles_coordinates:
        #     last_x, last_y = self.tiles_coordinates[-1]
        #     last_y += 1
        
        for i in range(len(self.tiles_coordinates) -1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]
                    
        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1
            
        # start_index = -int(self.V_NB_LINES / 2) + 1
        # end_index =  start_index + self.V_NB_LINES - 1
            
            
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r=random.randint(0,2)
            # 0 = straight
            # 1 = right
            # 2 = left
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2
                
            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x , last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x , last_y))
                
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x , last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x , last_y))
            last_y += 1
            # self.tiles_coordinates.append((last_x, last_y))
        
        
        
        
    def init_vertical_lines(self):
        # Initialize vertical lines with the canvas and color
        with self.canvas:
            Color(1, 1, 1)  # Set white color for the lines
            for i in range(0,self.V_NB_LINES):
                line = Line()  # Create a new line
                self.vertical_lines.append(line)  # Add line to the list
                
    def get_line_x_from_index(self,index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset*spacing + self.current_offset_x
        return line_x
    
    def get_line_y_from_index(self,index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y =  index*spacing_y - self.current_offset_y
        return line_y
        
    def get_tile_coordinates(self,tile_x,tile_y):
        tile_y = tile_y - self.current_y_loop
        x = self.get_line_x_from_index(tile_x)
        y = self.get_line_y_from_index(tile_y)
        return x,y
    
    def update_tiles(self):
        for i  in range(0,self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin , ymin = self.get_tile_coordinates(tile_coordinates[0] , tile_coordinates[1])
            xmax , ymax = self.get_tile_coordinates(tile_coordinates[0]+1 , tile_coordinates[1]+1)
            
            x1 , y1 = self.transform(xmin , ymin)
            x2 , y2 = self.transform(xmin , ymax)
            x3 , y3 = self.transform(xmax , ymax)
            x4 , y4 = self.transform(xmax , ymin)
            tile.points = [x1,y1,x2,y2,x3,y3,x4,y4]
            
    
    def update_vertical_lines(self):
        # Update the position of each vertical line based on screen size.abs
        start_index = -int(self.V_NB_LINES/2) + 1
        for i in range(start_index,start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1,y1 = self.transform(line_x, 0)
            x2,y2 = self.transform(line_x, self.height)
            
            
            self.vertical_lines[i].points = [x1, y1, x2, y2]  # Set points for each vertical line
            # offset += 1
## Horizontal Lines

    def init_horizontal_lines(self):
        # Initialize horizontal lines with the canvas and color
        with self.canvas:
            Color(1, 1, 1)  # Set white color for the lines
            for i in range(self.H_NB_LINES):
                line = Line()  # Create a new line
                self.horizontal_lines.append(line)  # Add line to the list

    def update_horizontal_lines(self):
        # Update the position of each horizontal line based on screen size
        # central_line_x = int(self.width / 2)
        # spacing = self.V_LINES_SPACING * self.width
        # offset = -int(self.V_NB_LINES / 2) + 0.5
        start_index = -int(self.V_NB_LINES/2) + 1
        end_index =  start_index + self.V_NB_LINES - 1
        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)
        
        for i in range(0,self.H_NB_LINES):
            line_y =  self.get_line_y_from_index(i)
            x1,y1 = self.transform(x_min, line_y)
            x2,y2 = self.transform(x_max, line_y) 
            self.horizontal_lines[i].points = [x1, y1, x2, y2]  # Set points for each vertical line
    
    def update(self, dt):
        # print("dt: " + str(dt*60))
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        
        if not self.state_game_over and self.state_game_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE: " + str(self.current_y_loop)
                self.generate_tiles_coordinates()
                print("loop : " + str(self.current_y_loop))

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "  G  A  M  E    O  V  E  R  "
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            print("GAME OVER")

    def on_menu_button_pressed(self):
        print("pressed")
        self.reset_game()
        self.state_game_started = True
        self.menu_widget.opacity = 0

        
class GalaxyApp(App):
    pass

GalaxyApp().run()
