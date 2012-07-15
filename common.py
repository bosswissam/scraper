# contains common methods/classes

# Start of rating types

class FiveStar:
    # score = average score out of 5
    # count = # of people who rated
    def __init__(self, score = -1, count = -1):
        self.five_star = score
        self.count = count

class Views:
    
    def __init__(self, count):
        self.views = count

class Favorers:
    
    def __init__(self, count):
        self.favorers = count

class Likes:
    
    def __init__(self, count):
        self.type = 'likes'
        self.count = count


# This class is for extensibility, so we don't have to create a class for each rating type
# (we never had to, but the previous ones where created for convenience and to enforce type
# names (e.g. 'likes', 'favorers'...))
class SimpleRating:
    
    def __init__(self):
        pass

# Start of Details objects

class Dimensions:
    
    def __init__(self, h, l, w, weight):
        self.type = 'dimensions'
        self.height = h
        self.length = l
        self.width = w
        self.weight = weight

class SimpleDetail:
    
    def __init__(self):
        pass

class SimpleObject:
    
    def __init(self):
        pass

# json.dumps is expecting a method, __dict__ is an attribute, hence this hack.
def serialize(x):
    return x.__dict__
