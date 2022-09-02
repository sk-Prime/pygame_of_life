#pylint:disable=W0621
import pygame
from random import randint
from sys import exit as sysexit
class Config():
    def __init__(self):
        self.screen_w = 720
        self.screen_h = 1440
        self.w = 300
        self.h = 300
        self.cell_size = 10
        self.gap = 2
        self.seamless=False
        self.resurrect = 3
        self.min_member = 2
        self.max_member = 3
        
        self.alive_col = (230,170,10)
        self.dead_col = (50,70,90)
        
        self.button_pos = 10,self.screen_h-150,150,100
        
    def add_screen_info(self,w,h):
        self.screen_w=w
        self.screen_h=h
conf = Config()

class Life():
    def __init__(self,x,y,grid:list):
        self.x = x
        self.y = y
        self.grid = grid
        
        self.__family_op=[
                        (-1,-1),(0,-1) ,(1,-1),
                        (-1,0)  ,(1,0),
                        (-1,1) ,(0,1)  ,(1,1)
                      ]
        
    @classmethod
    def create_from_conf(cls):
        x = conf.w//conf.cell_size
        y = conf.h//conf.cell_size
        grid = [[0]*x for _ in range(y)]
        return cls(x,y,grid)
    @classmethod
    def create_from_xy(cls,x,y):
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
        def replace(cell):
            if cell==0:
                return dead
            else:
                return life
        return "\n".join([" ".join(map(replace,row)) for row in self.grid])
        
    def random_point(self,n=50):
        for _ in range(n):
            x = randint(0,self.x-1)
            y=randint(0,self.y-1)
            self[x,y]=1
            
    def apply_rules(self,x,y):
        member=0
        cell = self[x,y]
        for ox,oy in self.__family_op:
            temp_x = x+ox
            temp_y = y+oy
            if not conf.seamless:
                if 0<temp_x<self.x and 0<temp_y<self.y:
                    if self[temp_x,temp_y]:
                        member+=1
            else:
                if temp_x<0:
                    temp_x=self.x-1
                elif temp_x >= self.x:
                    temp_x=0
                if temp_y<0:
                    temp_y=self.y-1
                elif temp_y>=self.y:
                    temp_y=0
                if self[temp_x,temp_y]:
                    member+=1
        if conf.min_member<=member<=conf.max_member and cell:
            return 1
        elif member==conf.resurrect and not cell:
            return 1
        else:
            return 0
    def test_glider(self,x,y):
        self[x,y+1] = 1
        self[x+1,y+2] = 1
        self[x+2,y+2] = 1
        self[x+2,y+1] = 1
        self[x+2,y] = 1
        
    def iteration(self):
        temp_grid= [[0]*self.x for _ in range(self.y)]
        for y in range(self.y):
            for x in range(self.x):
                temp_grid[y][x]=self.apply_rules(x,y)
        self.grid=temp_grid
        
class Life_2d(Life):
    def __init__(self,x,y,grid,screen):
        super().__init__(x,y,grid)
        self.screen = screen
        self.grid_x = 0
        self.grid_y = 0
        
        self.update_life = True
    @classmethod
    def create_from_conf(cls,screen):
        x = conf.screen_w//(conf.cell_size+conf.gap)
        y = conf.screen_h//(conf.cell_size+conf.gap)
        grid = [[0]*x for _ in range(y)]
        return cls(x,y,grid,screen)
        
    def calc_grid_position(self):
        self.grid_x = (conf.screen_w-(self.x*(conf.cell_size+conf.gap) - conf.gap))/2
        self.grid_y = (conf.screen_h-(self.y*(conf.cell_size+conf.gap) - conf.gap))/2
        
    def iteration(self):
        if self.update_life:
            temp_grid= [[0]*self.x for _ in range(self.y)]
        for y in range(self.y):
            for x in range(self.x):
                if self.update_life:
                    cell_state=self.apply_rules(x,y)
                    temp_grid[y][x]=cell_state
                else:
                    cell_state=self[x,y]
                    
                if cell_state:
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
        self.__draw = False
        
        self.font = pygame.font.SysFont("arial",30)
        
        self.bx,self.by,self.bw,self.bh = conf.button_pos
        self.play_button_srf = self.button("Play")
        self.draw_button_srf = self.button("Draw")
        
    def set_draw(self,switch):
        self.__draw=switch
        self.world.update_life=not switch
        
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
            
    def listen(self,mpos):
        px,py = mpos
        if self.bx<px<self.bx+self.bw and self.by<py<self.by+self.bh:
            self.screen.fill((0,0,0))
            self.__draw=not self.__draw
            self.world.update_life= not self.__draw
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
        conf.button_pos=0,conf.screen_h-50,100,50
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sysexit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.listen(event.pos)
        game.life_loop()
        pygame.display.flip()
    
