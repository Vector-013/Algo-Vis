import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("Dijkstra's visualizer")

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
GRAY = (190, 190, 190)
GREEN = (69,139,116)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
SILVER = (125,125,125)
YELLOW = (255, 255, 0)

class Vertex:
    def __init__(self,row,col,width,total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = BLACK
        self.adj = []
        self.width = width
        self.total_rows = total_rows
        
    def locate(self):
        return self.row,self.col
    
    def is_visited(self):
        return self.color == CYAN
    
    def is_open(self):
        return self.color == BLACK
    
    def is_blocker(self):
        return self.color == WHITE
    
    def is_start(self):
        return self.color == GREEN
    
    def is_end(self):
        return self.color == RED
    
    def mark_visited(self):
        self.color = CYAN
    
    def reset(self):
        self.color = BLACK
        
    def mark_open(self):
        self.color = PURPLE
    
    def mark_blocker(self):
        self.color = WHITE
        
    def mark_start(self):
        self.color = GREEN
        
    def mark_end(self):
        self.color = RED
    
    def make_path(self):
        self.color = ORANGE
        
    def draw(self,win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        
    def update_adj(self, grid):
        self.adj = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_blocker():  # DOWN
            self.adj.append(grid[self.row + 1][self.col])
            
        if self.row > 0 and not grid[self.row - 1][self.col].is_blocker():  # UP
            self.adj.append(grid[self.row - 1][self.col])
            
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_blocker():  # RIGHT
            self.adj.append(grid[self.row][self.col + 1])
            
        if self.row > 0 and not grid[self.row][self.col - 1].is_blocker():  # LEFT
            self.adj.append(grid[self.row][self.col - 1])
            
    def __lt__(self,other):
        return False

def reconstruct_path(start, end, back_track):
    curr = end
    
    while curr != start:
        back_track[curr].make_path()
        curr = back_track[curr]
   
    
def dijkstra(draw, grid, start, end):
    count = 0
    heap = PriorityQueue()
    heap.put((0, count, start))  ## count is a tie breaker, if two things have same dist, inserted first is popped
    back_track = {}
    dist = {vertex: float("inf") for row in grid for vertex in row}
    dist[start] = 0
    
    heap_hash = {start}  ## to check if something is in the priority queue
    
    while not heap.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        curr = heap.get()[2]
        
        heap_hash.remove(curr)
        if curr == end:
            curr.mark_end()
            reconstruct_path(start, end, back_track)
            start.mark_start()
            return True
        
        for neighbor in curr.adj:
            temp_dist = dist[curr] + 1
            
            if temp_dist < dist[neighbor]:
                back_track[neighbor] = curr
                dist[neighbor] = temp_dist
                
                if neighbor not in heap_hash:
                    count +=1
                    heap.put((dist, count, neighbor)) 
                    heap_hash.add(neighbor)
                    neighbor.mark_open()
                    
                    
        draw()
        
        if curr != start:
            curr.mark_visited()
            
    return False     
    

def make_grid(rows,width):
    grid = []      ## 2D list of Vertex objects
    gap = width // rows     ## width of each square
    
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Vertex(i, j, gap, rows)
            grid[i].append(spot)
            
    return grid


def draw_grid(win,rows,width):
    gap = width // rows 
    
    for i in range(rows):
        pygame.draw.line(win,SILVER, (0, i * gap), (width, i*gap))
        
    for j in range(rows):
        pygame.draw.line(win,SILVER, (j * gap, 0), (j*gap, width))
        
def draw(win, grid, rows, width):
    win.fill(BLACK)
    gap = width // rows
    
    for row in grid:
        for vertex in row:
            vertex.draw(win)
            
    for row in grid:
        row[0].mark_blocker()
        row[rows-1].mark_blocker()
        if row == grid[0]:
            for vertex in row:
                vertex.mark_blocker()
        if row == grid[rows - 1]:
            for vertex in row:
                vertex.mark_blocker()
            
            
    draw_grid(win, rows, width)
    pygame.display.update()
    
def get_cursor_pos(pos, rows, width):
    gap  = width // rows
    y,x = pos
    
    row = y//gap
    col = x// gap
    
    return row, col


def main(win, width):
    ROWS = 50
    
    grid = make_grid(ROWS, width)
    
    start = None
    end = None
    
    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if started:
                continue
            
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_cursor_pos(pos, ROWS, width)
                vertex = grid[row][col]
                if not start:
                    start = vertex
                    start.mark_start()
                    
                elif not end and vertex != start:
                    end = vertex 
                    end.mark_end()
                    
                elif vertex != end and vertex != start:
                    vertex.mark_blocker()
                
            elif pygame.mouse.get_pressed()[2]:  
                pos = pygame.mouse.get_pos()
                row, col = get_cursor_pos(pos, ROWS, width)
                vertex = grid[row][col]
                vertex.reset()
                if vertex == start:
                    start = None
                if vertex == end:
                    end = None
                    
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for vertex in row:
                            vertex.update_adj(grid)
                            
                    dijkstra(lambda: draw(win, grid, ROWS, width), grid, start, end)
            
    pygame.quit()
    
main(WIN, WIDTH)      

