class Cell:
    def render(self, screen, fill):
        for ix in range(self.get_width()):
            for iy in range(self.get_height()):
                screen[self.y0 + iy][self.x0 + ix] = fill

    def get_width(self):
        raise NotImplementedError

    def get_height(self):
        raise NotImplementedError

class Block(Cell):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
class Row(Cell):
    def __init__(self, *children):
        self.children = list(children)

    def get_width(self):
        return sum([c.get_width() for c in self.children])
    
    def get_height(self):
        return max([c.get_height() for c in self.children], default=0)
    
class Col(Cell):
    def __init__(self, *children):
        self.children = list(children)
    
    def get_width(self):
        return max([c.get_width() for c in self.children], default=0)
    
    def get_height(self):
        return sum([c.get_height() for c in self.children])

class Placing:
    def initialize_pos(self, x0=None, y0=None):
        self.x0 = x0
        self.y0 = y0
    

class PlacedBlock(Block, Placing):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.initialize_pos()
    
    def place(self, x0, y0):
        self.initialize_pos(x0=x0, y0=y0)
    
    def report(self):
        return[
            "block",
            self.x0, self.y0,
            self.x0 + self.width, self.y0 + self.height
        ]

class PlacedCol(Col,Placing):
    def __init__(self, *children):
        super().__init__(*children)
        assert isinstance(self.children, list)
        self.initialize_pos()

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
    def __init__(self,*children):
        super().__init__(*children)
        assert isinstance(self.children, list)
        self.initialize_pos()

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
    root.place(0,0)
    width = root.get_width()
    height = root.get_height()
    screen = make_screen(width, height)
    draw(screen, root)
    return "\n".join("".join(ch) for ch in screen)

def make_screen(width, height):
    screen = []
    for i in range(height):
        screen.append([""]* width)
    return screen

def draw(screen, node, fill=None):
    fill = next_fill(fill)
    node.render(screen, fill)
    if hasattr(node, "children"):
        for child in node.children:
            fill = draw(screen, child, fill)
    return fill

def next_fill(fill):
    return 'a' if fill is None else chr(ord(fill) +1)


class WrappedBlock(PlacedBlock):
    def wrap(self):
        return self

class WrappedCol(PlacedCol):
    def wrap(self):
        return PlacedCol(*[c.wrap() for c in self.children])

class WrappedRow(PlacedRow):
    def __init__(self, width, *children):
        super().__init__(*children)
        assert width >= 0, "Need non-negative width"
        self.width = width
    
    def get_width(self):
        return self.width
    
    def wrap(self):
        children = [c.wrap() for c in self.children]
        rows = self._bucket(children)
        new_rows = [PlacedRow(*r) for r in rows]
        new_col = PlacedCol(*new_rows)
        return PlacedRow(new_col)
    
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

        result.append(current_row)

        return result
    
