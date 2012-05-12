"""This module contains the utility data types of the DJ Scrooge Backtesting API.
Copyright (C) 2012  James Adam Cataldo

    This file is part of DJ Scrooge.

    DJ Scrooge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DJ Scrooge.  If not, see <http://www.gnu.org/licenses/>.
"""

class Node(object):
  """A doubly-linkned list node object"""
  next_node = None
  prev_node = None
  
  def __init__(self, value):
    """Construct a new Node with the given value."""
    self.value = value

class OrderedSet(object):
  """An ordered set with O(1) insert and delete operations.
  
  Note that the order of the elements is irrelevant, but there
  cannot contain duplicate elements. Trying to add an existing
  element to the set with cause an error.
  """
  
  def __init__(self):
    """Construct a new OrderedSet"""
    self.__hash_map = {}
    self.__head = None
    self.__tail = None
    self.__current = None
    self.__length = 0
    
  def __create_node(self, element):
    if self.__hash_map.has_key(element):
      raise KeyError('The set already contains the given element.')
    node = Node(element)
    self.__hash_map[element] = node
    self.__length += 1
    return node
  
  def __test_and_set_head(self, node):
    if self.__head is None:
      self.__head = node
      self.__tail = node
      return True
    return False
    
  def append(self, element):
    """Append an item to the end of the ordered set."""
    node = self.__create_node(element)
    if not self.__test_and_set_head(node):
      self.__tail.next_node = node
      node.prev_node = self.__tail
      self.__tail = node
      
  def prepend(self, element):
    """Prepend an item to the beginning of the ordered set."""
    node = self.__create_node(element)
    if not self.__test_and_set_head(node):
      self.__head.prev_node = node
      node.next_node = self.__head
      self.__head = node
      
  def insert_after(self, after_element, element):
    """Insert the given element after the after_element in the ordered set."""
    if not self.__hash_map.has_key(after_element):
      raise KeyError('The after_element is not in the OrderedSet.')
    node = self.__create_node(element)
    prev_node = self.__hash_map[after_element]
    node.prev_node = prev_node
    next_node = prev_node.next_node
    prev_node.next_node = node
    if next_node is None:
      self.__tail = node
    else:
      next_node.prev_node = node
      node.next_node = next_node
      
  def has_element(self, element):
    """Returns True if and only if the element is in the set."""
    return self.__hash_map.has_key(element)
  
  def remove(self, element):
    """Remove the givne element form the set."""
    if not self.__hash_map.has_key(element):
      raise KeyError('The given element is not in the set.')
    node = self.__hash_map[element]
    self.__length -= 1
    if node is self.__head and node is self.__tail:
      self.__head = None
      self.__tail = None
    elif node is self.__head:
      self.__head = self.__head.next_node
      self.__head.prev_node = None
    elif node is self.__tail:
      self.__tail = self.__tail.prev_node
      self.__tail.next_node = None
    else:
      next_node = node.next_node
      prev_node = node.prev_node
      prev_node.next_node = next_node
      next_node.prev_node = prev_node
    del self.__hash_map[element]
    
  def __iter__(self):
    """Identify this object as an iterator."""
    return self  
  
  def next(self):
    """Returned the next item when this sequence is being iterated."""
    if self.__current is None:
      self.__current = self.__head
    else:
      self.__current = self.__current.next_node
    if self.__current is None:
      raise StopIteration
    return self.__current.value
  
  def __len__(self):
    """Returnes the number of elements in teh set."""
    return self.__length
  
def iterator_to_list(iterator):
  """Given an arbitrary iterator, create a list of the values.
  
  Note that this should not be used for infinite iterators (streams).
  """
  result = []
  for x in iterator:
    result.append(x)
  return result

def index_of_sorted_list(element, sorted_list, left=0, right=None):
  """Returns the index of the given element in the sorted list, or -1 if the element is not found.
  
  This uses a binary search, so the list must be sorted on a data type for which comparison
  operators are well defined.
  """
  if right is None:
    right = len(sorted_list)
  while left < right:
    mid = (left+right) / 2
    midval = sorted_list[mid]
    if midval < element:
      left = mid+1
    elif midval > element: 
      right = mid
    else:
      return mid
  return -1
