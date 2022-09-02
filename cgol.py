import pygame
from random import randint
from sys import exit as sysexit
class Config():
    def __init__(self):
        #pygame given screen/surface width and height
        self.screen_w = 720 
        self.screen_h = 1440
        
        self.cell_size = 10

        
        #gap between cells
        self.gap = 2
        
        #Not seamless means all cell remain withing given self.screen
        #Seamless, can pass through one edge to another
        self.seamless=False
        
        #number of neighbouring members required to make a cell alive
        self.resurrect = 3
        #to remain alive,
        self.min_neighbour = 2
        self.max_neighbour = 3
        
        #color of cell
        self.alive_col = (230,170,10)
        self.dead_col = (50,70,90)
        
        self.button_pos = 10,self.screen_h-150,150,100
        self.clear_button_pos = 20+150,self.screen_h-150,150,100
    def add_screen_info(self,w,h):
        self.screen_w=w
        self.screen_h=h
conf = Config()

class Life():
    """This class is the base class. It does not depends on any window environment.
    It Does all the calculation on grids"""
    def __init__(self,x,y,grid:list):
        self.x = x #number of cell in x direction
        self.y = y #in y direction
        self.grid = grid #2d list. alive cell = 1, and dead cell = 0
        
        #to find neighbour of a given cell using x,y cords.
        self.__family_op=[
                        (-1,-1),(0,-1) ,(1,-1),
                        (-1,0)  ,(1,0),
                        (-1,1) ,(0,1)  ,(1,1)
                      ]
    @classmethod
    def create_from_size(cls,x,y):
        grid = [[0]*x for _ in range(y)]
        return cls(x,y,grid)
        
    def __getitem__(self,xy):
        x,y = xy
        return self.grid[y][x]
        
    def __setitem__(self,xy,value):
        x,y = xy
        self.grid[y][x]=value
        
    def __str__(self):
        return "\n".join([" ".join(map(str,row)) for row in self.grid])
    
    def ascii_repr(self,life='#',dead="."):
        #represent grid data in ascii characters. printing this in a loop
        # can simulate game of life in terminal.
        def replace(cell):
            if cell==0:
                return dead
            else:
                return life
        return "\n".join([" ".join(map(replace,row)) for row in self.grid])
        
    def random_point(self,n=50):
        #put alive cell in any random points
        for _ in range(n):
            x = randint(0,self.x-1)
            y=randint(0,self.y-1)
            self[x,y]=1
            
    def apply_rules(self,x,y):
        #rules of conway's game of life applied to given cell at x,y position
        neighbour=0
        cell = self[x,y] #value from grid
        for ox,oy in self.__family_op: #finding neighbour
            temp_x = x+ox
            temp_y = y+oy
            if not conf.seamless:
                if 0<temp_x<self.x and 0<temp_y<self.y:
                    if self[temp_x,temp_y]:
                        member+=1
            else:
                if temp_x<0: #move cell in right edge of given screen
                    temp_x=self.x-1
                elif temp_x >= self.x: #left edge
                    temp_x=0
                if temp_y<0: #bottom edge
                    temp_y=self.y-1
                elif temp_y>=self.y: #top edge
                    temp_y=0
                    
                if self[temp_x,temp_y]: #if neighbour is alive
                    neighbour+=1 #increasing member
        #neighbours are surviving range. not too or less populated
        if conf.min_neighbour<=neighbour<=conf.max_neighbour and cell:
            return 1 #remain 1 or alive
        elif neighbour==conf.resurrect and not cell:
            return 1 #dead cell become alive
        else: #all other cases cell will be dead.
            return 0
            
    def test_glider(self,x,y):
        #basic glider in x,y position for testing
        self[x,y+1] = 1
        self[x+1,y+2] = 1
        self[x+2,y+2] = 1
        self[x+2,y+1] = 1
        self[x+2,y] = 1
        
    def clear(self):
        #clear all cell
        self.grid= [[0]*self.x for _ in range(self.y)]
        
    def iteration(self):
        #main process
        #making empty grid state to store calculated outcome. 
        temp_grid= [[0]*self.x for _ in range(self.y)]
        for y in range(self.y):
            for x in range(self.x):
                temp_grid[y][x]=self.apply_rules(x,y)
        #assigning grid to new grid after applying rules.
        #next iteration will be on this latest situtation of the grid
        self.grid=temp_grid

class Life_2d(Life):
    def __init__(self,x,y,grid,screen):
        super().__init__(x,y,grid)
        self.screen = screen
        #cell/rect will be drawn from at this postion in a given screen.
        self.grid_x = 0 
        self.grid_y = 0
        
        self.update_life = True #to control game mode, playing or drawing
    @classmethod
    def create_from_conf(cls,screen):
        x = conf.screen_w//(conf.cell_size+conf.gap)
        y = conf.screen_h//(conf.cell_size+conf.gap)
        grid = [[0]*x for _ in range(y)]
        return cls(x,y,grid,screen)
        
    def calc_grid_position(self):
        #to make cell/rect at the middle of the screen.
        self.grid_x = (conf.screen_w-(self.x*(conf.cell_size+conf.gap) - conf.gap))/2
        self.grid_y = (conf.screen_h-(self.y*(conf.cell_size+conf.gap) - conf.gap))/2
        
    def iteration(self):
        if self.update_life:
            temp_grid= [[0]*self.x for _ in range(self.y)]
        for y in range(self.y):
            for x in range(self.x):
                if self.update_life:
                    #update life means apply rules
                    cell_state=self.apply_rules(x,y)
                    temp_grid[y][x]=cell_state
                else:
                    #just draw cell as it is in the self.grid.
                    cell_state=self[x,y]
                    
                if cell_state: #True=1=alive
                    color = conf.alive_col
                else:
                    color=conf.dead_col
                    
                pygame.draw.rect(self.screen,color,(self.grid_x+x*(conf.cell_size+conf.gap),self.grid_y+y*(conf.cell_size+conf.gap),conf.cell_size,conf.cell_size))
                
        if self.update_life:
            self.grid=temp_grid

class Game():
    def __init__(self,screen):
        self.screen = screen
        self.world = Life_2d.create_from_conf(self.screen)
        self.world.calc_grid_position()
        self.__draw = False #drawing mode or playing mode
        
        self.font = pygame.font.SysFont("arial",30)
        
        self.bx,self.by,self.bw,self.bh = conf.button_pos
        self.cx,self.cy,self.cw, self.ch = conf.clear_button_pos
        self.play_button_srf = self.button("Play")
        self.draw_button_srf = self.button("Draw")
        self.clear_button_srf = self.button("Clear")
        
    def set_draw(self,switch):
        self.__draw=switch #if drawing mode = true
        self.world.update_life=not switch #update_life = false
        
    def button(self,name):
        button_srf = pygame.Surface((self.bw,self.bh))
        button_srf.set_colorkey((0))
        pygame.draw.rect(button_srf,(255,255,255),(0,0,self.bw,self.bh),width=2)
        text = self.font.render(name,3,(255,255,255))
        tx,ty = text.get_size()
        text_x = self.bw/2 - tx/2
        text_y = self.bh/2 - ty/2
        button_srf.blit(text,(text_x,text_y))
        return button_srf
            
    def random_cell(self,n=1000):
        self.world.random_point(n)
    
    def life_loop(self):
        self.world.iteration()
        self.buttons_render()
        
    def buttons_render(self):
        if self.__draw:
            self.screen.blit(self.play_button_srf,(self.bx,self.by))
        else:
            self.screen.blit(self.draw_button_srf,(self.bx,self.by))
        self.screen.blit(self.clear_button_srf,(self.cx,self.cy))
            
    def listen(self,mpos):
        px,py = mpos
        if self.bx<px<self.bx+self.bw and self.by<py<self.by+self.bh:
            self.screen.fill((0,0,0))
            self.set_draw(not self.__draw)

        elif self.cx<px<self.cx+self.cw and self.cy<py<self.cy+self.ch:
            self.world.clear()
            self.set_draw(True) #clearing so enabling drawing
        else:
            x = int((px-self.world.grid_x) //(conf.cell_size+conf.gap))
            y = int((py-self.world.grid_y) //(conf.cell_size+conf.gap))
            if 0<=x<self.world.x and 0<=y<self.world.y:
                self.world[x,y] = not self.world[x,y]




if __name__=="__main__":
    pygame.init()
    in_pc = True
    if in_pc:
        conf.add_screen_info(600,600)
        conf.button_pos=0,conf.screen_h-50,100,35
        conf.clear_button_pos=120,conf.screen_h-50,100,35
    else:
        conf.add_screen_info(720,1440)
    
    screen = pygame.display.set_mode((conf.screen_w,conf.screen_h))
    
    conf.seamless=True
    conf.cell_size=15
    conf.gap=1

    game=Game(screen)
    game.set_draw(True)
    #game.random_cell(n=100)
    
    while True:
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sysexit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.listen(event.pos)
        game.life_loop()
        pygame.display.flip()
