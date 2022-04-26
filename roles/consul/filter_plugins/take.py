def take_n_number_of_elements(list, n):
    return list[0:n]
class FilterModule(object):
    def filters(self):
      return {'take': take_n_number_of_elements}