class Line:
    def __init__(self, color, start_pos, end_pos, width):
        self.color = color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = width

    def update(self, color, start_pos, end_pos, width):
        self.color = color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = width

    def stringify(self):
       return str(self.color) + "," + str(self.start_pos) + "," + str(self.end_pos) + "," + str(self.width)

    def print(self):
        print(f"color = {self.color}, start pos = {self.start_pos}, end pos = {self.end_pos}, width = {self.width}")