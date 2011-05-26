import logging as log
import datetime
import random
import time


class Resource(object):

  def __init__(self, name=''):
    self.name = name
    self.created = datetime.datetime.now()
    log.info('Resource created: %s', self)

  def __str__(self):
    return '<Resource name="%s" created="%s">' % (self.name, self.created)


class MissException(Exception):
  """ A very glamorous exception.
  """
  def __init__(self):
    super(MissException, self).__init__()
    log.info('MissException happened')

class Container(list):

  def __init__(self, name, parent):
    super(Container, self).__init__()
    self.name = name
    self.parent = parent
    log.info('Container created: %s', self)

  def __str__(self):
    return '<Container name="%s" items="%d">' % (self.name, len(self))

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
      item = super(Container, self).pop()
      log.info('%s: pop()d one item (%s)', self, item)
      return item

    # No available resources, retrieve it and signal a miss
    log.info('%s: retrieving from parent', self)
    self.append(self.parent.pop())
    raise MissException()


class InfiniteContainer(Container):

  def __init__(self, name, item_class):
    super(InfiniteContainer, self).__init__(name, None)
    self.item_class = item_class

  def __str__(self):
    return '<InfiniteContainer name="%s" items="oo">' % (self.name)

  def pop(self):
    return self.item_class('item-%d' % len(self))



class AbsoluteJITStrategySimulation(object):

  def __init__(self):
    self.remote_supply = InfiniteContainer('Remote Supply', Resource)
    self.local_storage = Container('Local Storage', self.remote_supply)
    self.satisfied = 0
    self.misses = 0

  def incr_satisfied(self):
    log.info('Client got satisfied')
    self.satisfied += 1

  def incr_wait(self):
    log.info('Client has to wait')
    self.misses += 1

  def reset(self):
    self.satisfied = 0
    self.misses = 0

  def run(self):
    """ The absolute Just-in-Time strategy basically tries to keep
    local storage with only one item. Once it's consumed, ask for another.

    This simulation is useless. Use the skeleton to build better simulations.
    """
    while True:
      # Normal with mean=100, std_deviation=10
      n_requested = int(random.normalvariate(1000, 100))

      for i in range(n_requested):
        try:
          client = self.local_storage.pop()
          self.incr_satisfied()
        except MissException:
          self.incr_wait()

      print 'In one round, got %d misses, %d satisfied' % (self.misses, self.satisfied)
      #self.reset()
      time.sleep(0.1)


def test_infinite_container(self):
  print 'Testing infinite supply'
  origin = InfiniteContainer('Supplier', Resource)
  c = Container('Local Storage', origin)
  assert isinstance(origin.pop(), Resource), 'Supplier is not generating the appropriate resources'

if __name__ == '__main__':
  log.basicConfig(level=log.INFO)

  try:
    AbsoluteJITStrategySimulation().run()
  except KeyboardInterrupt:
    print 'Exiting'
