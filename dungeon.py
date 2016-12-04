import random
import pygame
import numpy

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (180,180,190)
DARK_GREY=(50,50,50)

margin=40
circle_diam=10
line_width=3
w, h = 15, 15

pygame.init()
width=(h+1)*margin #it's backwards, I know, but I can't be bothered to fix the error in the code.
height=(w+1)*margin
size = (width,height)
screen = pygame.display.set_mode(size) 
pygame.display.set_caption("Dungeon Mapper")
done = False
clock = pygame.time.Clock()
paused=False
#paused=True
stopped=False


nodelist = numpy.zeros((h,w))
fill_percent=0.5

def addnode(coordinates):
    nodelist[coordinates[0]][coordinates[1]]=1

starting_point=[random.randrange(0,h),random.randrange(0,w)]
addnode(starting_point)

connections_list=[]

def one_away(coordinates):
    '''
    Given a set of coordinates, return all the nodes that immediately 
    surround it.
    '''
    check_list=[]
    for i in range(-1,2):
        for j in range(-1,2):
            if [i,j]!=[0,0] and 0<=coordinates[0]+i<h and 0<=coordinates[1]+j<w: #not self, not off the edge
                check_list.append([coordinates[0]+i,coordinates[1]+j])
    return(check_list)

def empty_nodes():
    '''
take every non-empty node in nodelist, check all the surrounding empty
nodes, and return the coords of a non-empty node with the highest 
number of empty surrounding nodes
'''
    coord_dict={}
    nonzero=numpy.transpose(numpy.nonzero(nodelist))
    for entry in nonzero:
        counter=0
        for i in one_away(entry):
            if nodelist[i[0]][i[1]]==0:
                counter+=1
        coord_dict[tuple(entry)]=counter
    for k,v in list(coord_dict.items()):
        if v<max(coord_dict.values()):
            del coord_dict[k]
    return (random.choice(list(coord_dict.keys())))

def connect_new_nodes():
    selected_node=empty_nodes()
    selected_one_away=random.choice(one_away(selected_node))
    addnode(selected_one_away)
    connections_list.append([selected_node,selected_one_away])

def convert_to_screen(coordinate):
    return (coordinate+1)*margin

def drawcircles():
    for row in range(w):
        for column in range(h):
            if nodelist[column][row]==1:
                pygame.draw.circle(screen,BLACK,[convert_to_screen(column),convert_to_screen(row)],circle_diam,0)
                pygame.draw.circle(screen,WHITE,[convert_to_screen(column),convert_to_screen(row)],circle_diam,1)
                
def drawlines():
    
    for connection in connections_list:
        pygame.draw.line(screen, LIGHT_GREY, [convert_to_screen(connection[0][0]),
        convert_to_screen(connection[0][1])],[convert_to_screen(connection[1][0]),
        convert_to_screen(connection[1][1])], line_width)

def drawgrid():
    for i in range(1,h+1):
        pygame.draw.line(screen, DARK_GREY, (i*margin,margin),(i*margin,w*margin))
    for j in range(1,w+1):
        pygame.draw.line(screen, DARK_GREY, (margin,j*margin),(h*margin,j*margin))

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                done=True
            #paused=False
    if paused==False and stopped==False:
        connect_new_nodes()
        screen.fill(BLACK)
        drawgrid()
        drawlines()
        drawcircles()
        pygame.display.flip()
        clock.tick(60)
        #paused=True
    if sum(sum(nodelist))>w*h*fill_percent:
        stopped=True


pygame.quit()
