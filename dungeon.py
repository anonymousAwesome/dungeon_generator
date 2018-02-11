'''
The workflow is a little funky. First the program generates the dungeon,
then it waits. Once you press any key it takes any dead-ends and
integrates them into the rest of the dungeon, though it won't do this if
there are no nodes close enough to the dead-end, or if the nearby nodes
would be at too steep an angle.

Press Return to end the program.
'''

import random
import pygame
import numpy
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (180,180,190)
DARK_GREY=(50,50,50)

margin=40
circle_diam=10
circle_line_width=3
line_width=3
grid_line_width=1
w, h = 15, 15
fill_percent=0.8
diagonal_percent=.25

pygame.init()
width=(h+1)*margin #it's backwards, I know, but I can't be bothered to fix the error in the code.
height=(w+1)*margin
size = (width,height)
screen = pygame.display.set_mode(size) 
pygame.display.set_caption("Dungeon Mapper")
done = False
clock = pygame.time.Clock()
paused=False
stopped=False
phase="drawing"

nodelist = numpy.zeros((h,w))

def addnode(coordinates):
    nodelist[coordinates[0]][coordinates[1]]=1

starting_point=[random.randrange(0,h),random.randrange(0,w)]
addnode(starting_point)

connections_list=[]

def one_away(coordinates,diagonal_percent=diagonal_percent):
    '''
    Given a set of coordinates, return all the nodes that immediately 
    surround it.
    '''
    check_list=[]
    for i in range(-1,2):
        for j in range(-1,2):
            if random.random()<diagonal_percent or i*j==0:
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

def connection_check(coords1,coords2):
    if [coords1,coords2] in connections_list or [coords2,coords1] in connections_list:
        return True
    else:
        return False

def cross_check(coords1,coords2):
    if abs((coords1[0]-coords2[0])*(coords1[1]-coords2[1]))==1: #diagonal
        swapped_one=[coords1[0],coords2[1]]
        swapped_two=[coords2[0],coords1[1]]
        if connection_check(swapped_one,swapped_two):
           return True
    return False

def connect_new_nodes():
    while True:
        selected_node=list(empty_nodes())
        selected_one_away=random.choice(one_away(selected_node))
        if not connection_check(selected_node,selected_one_away): #prevents redundant nodes
            if not cross_check(selected_node,selected_one_away): #prevents crossed nodes
                addnode(selected_one_away)
                connections_list.append([selected_node,selected_one_away])
                break

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given
    origin, then rounds the result.
    The angle should be given in degrees.
    """
    angle=math.radians(angle)
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return ([round(qx), round(qy)])

def one_connection_nodes():
    '''
Take a list of non-empty nodes and check each node to see if it has exactly one connection.
If it does, return the center node and the edge node for each of the one-connection nodes.
    '''
    nonzero=numpy.transpose(numpy.nonzero(nodelist))
    temp_list=[]
    for entry in nonzero:
        connect_nodes=one_away(entry,1)
        connection_count=0
        for node in connect_nodes:
            if connection_check(node,entry.tolist()):
                connection_count+=1
                last_check=node
        if connection_count==1:
            temp_list.append([entry.tolist(),last_check])
    return temp_list


def connect_existing_nodes():
    '''
Find each node that has only one connection.  - done
Find the coordinates of the node it's connected to. - done
Find the coordinates for the node in the exact opposite direction and 
 see if there's a node there. 
If so, connect them and move on.
If not, find the coordinates for the two nodes 45 degrees 
(one segment away) from the previous check.  
If one of them has a node, connect it.  
If they both have nodes, randomly select one and connect it.
Do the same thing again, at 90-degree angles (2 segments) from the 
initial check.
Don't go any further than 90 degrees.
    '''
    nonzero=numpy.transpose(numpy.nonzero(nodelist)).tolist()
    for node_pair in one_connection_nodes():
        opposite=rotate(node_pair[0],node_pair[1],180)
        cw1=rotate(node_pair[0],node_pair[1],135) #no idea which of these are clockwise/counterclockwise.
        ccw1=rotate(node_pair[0],node_pair[1],225)
        cw2=rotate(node_pair[0],node_pair[1],90)
        ccw2=rotate(node_pair[0],node_pair[1],270)
        if opposite in nonzero:
            if not cross_check(node_pair[0],opposite):
                connections_list.append([node_pair[0],opposite])
        elif cw1 in nonzero and ccw1 in nonzero:
            chosen=random.choice([cw1,ccw1])
            if not cross_check(node_pair[0],chosen):
                connections_list.append([node_pair[0],chosen])
        elif cw1 in nonzero:
            if not cross_check(node_pair[0],cw1):
                connections_list.append([node_pair[0],cw1])
        elif ccw1 in nonzero:
            if not cross_check(node_pair[0],ccw1):
                connections_list.append([node_pair[0],ccw1])
        elif cw2 in nonzero and ccw2 in nonzero:
            chosen=random.choice([cw2,ccw2])
            if not cross_check(node_pair[0],chosen):
                connections_list.append([node_pair[0],chosen])
        elif cw2 in nonzero:
            if not cross_check(node_pair[0],cw2):
                connections_list.append([node_pair[0],cw2])
        elif ccw2 in nonzero:
            if not cross_check(node_pair[0],ccw2):
                connections_list.append([node_pair[0],ccw2])
 
def convert_to_screen(coordinate):
    return (coordinate+1)*margin

def drawcircles():
    for row in range(w):
        for column in range(h):
            if nodelist[column][row]==1:
                pygame.draw.circle(screen,BLACK,[convert_to_screen(column),convert_to_screen(row)],circle_diam,0)
                pygame.draw.circle(screen,WHITE,[convert_to_screen(column),convert_to_screen(row)],circle_diam,circle_line_width)
                
def drawlines():
    
    for connection in connections_list:
        pygame.draw.line(screen, LIGHT_GREY, [convert_to_screen(connection[0][0]),
        convert_to_screen(connection[0][1])],[convert_to_screen(connection[1][0]),
        convert_to_screen(connection[1][1])], line_width)

def drawgrid():
    for i in range(1,h+1):
        pygame.draw.line(screen, DARK_GREY, (i*margin,margin),(i*margin,w*margin),grid_line_width)
    for j in range(1,w+1):
        pygame.draw.line(screen, DARK_GREY, (margin,j*margin),(h*margin,j*margin),grid_line_width)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                done=True
            paused=False
    if phase=="drawing":
        connect_new_nodes()
        screen.fill(BLACK)
        drawgrid()
        drawlines()
        drawcircles()
        pygame.display.flip()
        clock.tick(60)
        if sum(sum(nodelist))>w*h*fill_percent:
            phase="connecting"
            paused=True

    if phase=="connecting" and paused==False:
        connect_existing_nodes()
        drawlines()
        drawcircles()
        pygame.display.flip()
        paused=True
pygame.quit()
