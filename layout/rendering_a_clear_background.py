class Cell:
    """this is the base representation of the attributes of a display unit"""
    def __init__(self):
        self.has_content = False
    
    def set_content(self, content, x, y):
        self.content = content
        self.content_x = x
        self.content_y = y
        self.has_content = True
    
    def get_content_pos(self):
        return (self.content_x, self.content_y)
    
    def get_content(self):
        return self.content
    
    def get_width(self):
        raise NotImplementedError

    def get_height(self):
        raise NotImplementedError

class Block(Cell):
    """this represents the basic unit of display"""
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height

    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
class Row(Cell):
    """this is a representation of the row of a display"""
    def __init__(self, children):
        super().__init__()
        self.children = list(children)

    def get_width(self):
        return sum([c.get_width() for c in self.children])
    
    def get_height(self):
        return max([c.get_height() for c in self.children], default=0)
    
class Col(Cell):
    """this is the representation of the column of a display"""
    def __init__(self, children):
        super().__init__()
        self.children = list(children)
    
    def get_width(self):
        return max([c.get_width() for c in self.children], default=0)
    
    def get_height(self):
        return sum([c.get_height() for c in self.children])

class Placing:
    """this adds placing attributes (coordinates)"""
    def initialize_pos(self, x0=None, y0=None):
        self.x0 = x0
        self.y0 = y0
    

class PlacedBlock(Block, Placing):
    def __init__(self, width, height):
        Block.__init__(self, width, height)
        Placing.initialize_pos(self)
    
    def place(self, x0, y0):
        self.initialize_pos(x0=x0, y0=y0)
    
    def report(self):
        return[
            "block",
            self.x0, self.y0,
            self.x0 + self.width, self.y0 + self.height
        ]

class PlacedCol(Col, Placing):
    def __init__(self, children):
        Col.__init__(self, children)
        Placing.initialize_pos(self)

    def place(self, x0, y0):
        self.initialize_pos(x0=x0, y0=y0)
        y_current = self.y0
        for child in self.children:
            child.place(x0, y_current)
            y_current += child.get_height()

    def report(self):
        return [
            "col",
            self.x0, self.y0,
            self.x0 + self.get_width(), self.y0 + self.get_height(),
        ] + [c.report() for c in self.children]

class PlacedRow(Row, Placing):
    def __init__(self, children):
        Row.__init__(self, children)
        Placing.initialize_pos(self)

    def place(self, x0, y0):
        self.initialize_pos(x0=x0, y0=y0)
        y1 = self.y0 + self.get_height()
        x_current = x0
        for child in self.children:
            child_y = y1 - child.get_height()
            child.place(x_current, child_y)
            x_current += child.get_width()
    
    def report(self):
        return [
            "row",
            self.x0,
            self.y0,
            self.x0 + self.get_width(),
            self.y0 + self.get_height(),
        ] + [c.report() for c in self.children]


def render(root):
    root.place(0, 0)
    width = root.get_width()
    height = root.get_height()
    screen = make_screen(width, height)
    draw(screen, root)
    return "\n".join("".join(ch if ch is not None else ' ' for ch in row) for row in screen)

def make_screen(width, height):
    return [[''] * width for _ in range(height)]

def draw(screen, node, fill=None):
    fill = next_fill(fill)
    node.render(screen, fill)
    if hasattr(node, "children"):
        for child in node.children:
            fill = draw(screen, child, fill)
    return fill

def next_fill(fill):
    return 'a' if fill is None else chr(ord(fill) + 1)

def render_obj(screen, fill, obj):
    for iy in range(obj.get_height()):
        for ix in range(obj.get_width()):
            current_x = obj.x0 + ix
            current_y = obj.y0 + iy
            # GVW: can the `obj.has_content` test be moved up to the top
            # of the method so it's not repeated inside the loop? I.e.,
            # can the method start with `if not obj.has_content: return`
            # or something like that? Why or why not?
            if obj.has_content and obj.intersect_content(current_x, current_y):
                content_index = current_x - obj.content_x
                screen[current_y][current_x] = obj.get_content()[content_index]

class Renderable:
    def render(self, screen, fill):
        render_obj(screen, fill,obj=self)
        if hasattr(self, 'children'):
            for child in self.children:
                render_obj(screen, fill, child)
        
    def intersect_content(self, current_x, current_y):
        content_x, content_y = self.get_content_pos()
        return (
            current_x >= content_x and 
            current_x < content_x + len(self.get_content()) and 
            current_y == content_y
        )

class RenderedBlock(PlacedBlock, Renderable):
    pass

class RenderedCol(PlacedCol, Renderable):
    pass

class RenderedRow(PlacedRow, Renderable):
    pass

class WrappedBlock(PlacedBlock):
    def wrap(self):
        return self

class WrappedCol(PlacedCol):
    def wrap(self):
        return WrappedCol([c.wrap() for c in self.children])

class WrappedRow(PlacedRow):
    def __init__(self, width, *children):
        super().__init__(children)
        assert width >= 0, "Need non-negative width"
        self.width = width
    
    def get_width(self):
        return self.width
    
    def wrap(self):
        if self.width < sum([child.get_width() for child in self.children]):
            children = [c.wrap() for c in self.children]
            rows = self._bucket(children)
            new_rows = [PlacedRow(r) for r in rows]
            new_col = PlacedCol(new_rows)
            return WrappedCol([new_col])
        else:
            return self
    
    def _bucket(self, children):
        result = []
        current_row = []
        current_x = 0

        for child in children:
            child_width = child.get_width()
            if (current_x + child_width) <= self.width:
                current_row.append(child)
                current_x += child_width
            else:
                result.append(current_row)
                current_row = [child]
                current_x = child_width

        if current_row:
            result.append(current_row)

        return result
    

if __name__ == '__main__':
    rb = RenderedBlock(6, 6)
    rb.set_content('how', 1, 2)
    rw = RenderedRow([rb])
    rw.place(0, 0)
    rw.set_content('you', 3,4)
    screen = make_screen(10, 10)
    rw.render(screen, 'a')
    for row in screen:
        print(row)
