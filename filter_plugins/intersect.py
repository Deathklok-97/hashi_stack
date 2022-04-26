def a_intersect_b(a, b):
    return list(set(a) & set(b))

class FilterModule(object):
    def filters(self):
      return {'intersect': a_intersect_b}