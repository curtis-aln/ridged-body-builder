import pygame as pg

from pygame import Vector2, Rect


class Node:
    def __init__(self, position : Vector2) -> None:
        self.position = position
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        self.mass : float = 0.0
        self.radius : float = 5.0
        self.color = (255, 0, 0)
    

    def update(self, dt : float) -> None:
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.acceleration = Vector2(0, 0)


class Spring:
    def __init__(self, nodeA : Node, nodeB : Node, internal=False) -> None:
        self.internal = internal
        self.nodeA = nodeA
        self.nodeB = nodeB

        self.length : float = 0.0
        self.restLength : float = (self.nodeA.position - self.nodeB.position).length()
        self.color = (255, 255, 255)
        self.k : float = 0.0
        self.d : float = 0.0
    

    def update(self, dt : float) -> None:
        self.length = (self.nodeA.position - self.nodeB.position).length()
        self.acceleration = (self.nodeA.position - self.nodeB.position).normalize() * (self.length - self.restLength) * self.k  
        self.nodeA.acceleration += self.acceleration
        self.nodeB.acceleration -= self.acceleration    


class RidgedBody:
    def __init__(self) -> None:
        self.nodes : list[Node] = []
        self.springs : list[Spring] = []

        # if the body is locked then it cannot be moved
        self.locked = False

        self.bounding_box = Rect(0, 0, 0, 0)


    def add_node(self, x: float, y: float) -> None:
        self.nodes.append(Node(Vector2(x, y)))
    
    def add_spring(self, indexA : int, indexB : int, internal=False) -> None:
        self.springs.append(Spring(self.nodes[indexA], self.nodes[indexB],internal))
    

    def set_center(self, new_center) -> None:
        center = Vector2(new_center)
        current_center = self.get_center()
        direction = center - current_center

        for node in self.nodes:
            node.position += direction
    

    def lock(self): self.locked = True
    def unlock(self): self.locked = False
    

    def update(self, dt : float) -> None:
        self.bounding_box = self.get_bounding_box()

        for spring in self.springs:
            spring.update(dt)
        
        for node in self.nodes:
            node.update(dt)
    

    def render(self, window, debug : bool = False, highlight = False) -> None:
        HIGHLIGHT_COL = (20, 55, 205)
        THICKNESS = 3

        for spring in self.springs:
            color = HIGHLIGHT_COL if highlight else spring.color
            if not (spring.internal and not debug):
                pg.draw.line(window, color, spring.nodeA.position, spring.nodeB.position, THICKNESS)
        
        if debug:
            for node in self.nodes:
                pg.draw.circle(window, node.color, (int(node.position.x), int(node.position.y)), int(node.radius))

            # rendering the bounding box and center
            bounding_box_col = (70, 70, 70)
            pg.draw.rect(window, bounding_box_col, self.bounding_box, THICKNESS)

            pg.draw.circle(window, bounding_box_col, self.get_center(), 5)


    def contains_point(self, position) -> bool:
        x, y = position
        num_vertices = len(self.nodes)
        odd_intersections = False
        
        for i in range(num_vertices):
            j = (i + 1) % num_vertices
            xi, yi = self.nodes[i].position
            xj, yj = self.nodes[j].position
            
            # Check if the point is on an edge of the polygon
            if (yi > y) != (yj > y):
                intersect_x = (xj - xi) * (y - yi) / (yj - yi) + xi
                if x < intersect_x:
                    odd_intersections = not odd_intersections
        
        return odd_intersections

        
    def collision_detection(self, ridged_body) -> bool:
        # checks if there is a collision between this body and the ridged body

        # first we return false if the two bounding boxes are not touching
        bounding_box_1 = self.bounding_box
        bounding_box_2 = ridged_body.bounding_box
        if not bounding_box_1.colliderect(bounding_box_2):
            return False
        
        # now that they are touching we see if any lines overlap

    

    def get_bounding_box(self):
        # returns a rect which describes the bounding box of the body by finding the two points furthest from each other
        # and the two points furthest from each other on the opposite side of the rect
        if len(self.nodes) == 0:
            return Rect(0, 0, 0, 0)

        max_x, max_y = self.nodes[0].position
        min_x, min_y = self.nodes[0].position

        for node in self.nodes:
            if node.position.x > max_x:
                max_x = node.position.x
            if node.position.x < min_x:
                min_x = node.position.x
            if node.position.y > max_y:
                max_y = node.position.y
            if node.position.y < min_y:
                min_y = node.position.y
        
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)


    def get_center(self):
        # gets the center of the shape
        return Vector2(self.bounding_box.x + self.bounding_box.width / 2, self.bounding_box.y + self.bounding_box.height / 2)   



# turns a rectangle (x,y,w,h) into a ridged body object
def ridged_body_from_rect(rect : tuple):
    body = RidgedBody()
    body.add_node(rect[0], rect[1])
    body.add_node(rect[0] + rect[2], rect[1])  
    body.add_node(rect[0] + rect[2], rect[1] + rect[3])
    body.add_node(rect[0], rect[1] + rect[3])
    body.add_spring(0, 1)
    body.add_spring(1, 2)
    body.add_spring(2, 3)
    body.add_spring(3, 0)

    # diagonal connections
    body.add_spring(0, 2, internal=True)
    body.add_spring(1, 3, internal=True)

    return body