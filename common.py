# contains common methods/classes

# Start of rating types

class FiveStar:
    # score = average score out of 5
    # count = # of people who rated
    def __init__(self, score = -1, count = -1):
        self.type = 'five_star' # this is just a hack to get the type to print in __dict__
        self.score = score
        self.count = count

class Views:
    
    def __init__(self, count):
        self.type = 'views'
        self.count = count

class Favorers:
    
    def __init__(self, count):
        self.type = 'favorers'
        self.count = count

class Likes:
    
    def __init__(self, count):
        self.type = 'likes'
        self.count = count


# This class is for extensibility, so we don't have to create a class for each rating type
# (we never had to, but the previous ones where created for convenience and to enforce type
# names (e.g. 'likes', 'favorers'...))
class SimpleRating:
    
    def __init__(self, rating_type, count):
        self.type = rating_type
        self.count = count

    def __init__(self):
        self.x = 's'

# Start of Details objects

class Dimensions:
    
    def __init__(self, h, l, w, weight):
        self.type = 'dimensions'
        self.height = h
        self.length = l
        self.width = w
        self.weight = weight

class SimpleDetail:
    
    def __init__(self, detail_type, value):
        self.type = detail_type
        self.value = value

# json.dumps is expecting a method, __dict__ is an attribute, hence this hack.
def serialize(x):
    return x.__dict__
