import logging as log
import datetime


class Resource(object):

  def __init__(self, name=''):
    self.name = name
    self.created = datetime.datetime.now()
    log.info('%s created at %s', name, str(self.created))

class MissException(Exception):
  """ A very glamorous exception.
  """
  def __init__(self):
    super(MissException, self).__init__()
    log.info('%s happened', self)

class Container(list):

  def __init__(self, name, parent):
    super(Container, self).__init__()
    self.name = name
    self.parent = parent
    log.info('%s created at %s', self, datetime.datetime.now())

  def pop(self):
    """ Attempt to get a resource unity from this container or request
    from parent.

    Cases:
      Container not empty:
        - means len(self) != 0
        - pop() will retrieve the last resource on this
      Container empty:
        - means len(self) == 0
        - pop() will attempt to retrieve a resource, but will fail
          - failure will be signaled by raising MissException()
        - pop() will attempt to retrieve from parent container in "background"
    """
    if len(self) != 0:
      # We have available resources
      return super(Container, self).pop()

    # No available resources, retrieve it and signal a miss
    self.append(self.parent.pop())
    raise MissException()


class InfiniteContainer(Container):

  def __init__(self, name, item_class):
    super(InfiniteContainer, self).__init__(name, None)
    self.item_class = item_class

  def pop(self, index=0):
    return self.item_class()

if __name__ == '__main__':
  origin = InfiniteContainer('Supplier', Resource)
  c = Container('Local Storage', origin)

  assert isinstance(origin.pop(), Resource), 'Supplier is not generating the appropriate resources'
