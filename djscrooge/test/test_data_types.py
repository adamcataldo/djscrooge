"""This module contains tests for the data_types module of the DJ Scrooge backtesting API.
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

Dependencies: 
    proboscis: <https://github.com/rackspace/python-proboscis>
"""
from proboscis import test
from proboscis.asserts import assert_equal
from proboscis.asserts import assert_true
from proboscis.asserts import assert_false
from proboscis.asserts import assert_raises
from djscrooge.data_types import OrderedSet
from djscrooge.data_types import iterator_to_list
from djscrooge.data_types import index_of_sorted_list

@test
class TestOrderedSet(object):
  """Test the OrderedSet class."""

  def create_basic_set(self):
    my_set = OrderedSet()
    my_set.append(1)
    my_set.append(2)
    my_set.append(3)
    return my_set

  @test(groups=['size_modifier'])
  def test_append(self):
    """Test the append method of OrderedSet."""
    my_set = self.create_basic_set()
    x = 1
    for element in my_set:
      assert_equal(element, x)
      x = x + 1
    assert_equal(4, x, 'Expected set to have 3 items.')
    assert_raises(KeyError, my_set.append, 3)
    
  @test(groups=['size_modifier'])
  def test_prepend(self):
    """Test the prepend method of OrderedSet."""
    my_set = OrderedSet()
    my_set.prepend(1)
    my_set.prepend(2)
    my_set.prepend(3)
    x = 3
    for element in my_set:
      assert_equal(element, x)
      x = x - 1
    assert_equal(0, x, 'Expected set to have 3 items.')
    assert_raises(KeyError, my_set.prepend, 3)
    
  @test(groups=['size_modifier'], depends_on=['test_append'])
  def test_insert_after(self):
    """Test the insert_after method of OrderedSet."""
    my_set = self.create_basic_set()
    my_set.insert_after(1, 4)
    x = 0
    expected = [1, 4, 2, 3]
    for element in my_set:
      assert_equal(element, expected[x])
      x = x + 1
    assert_equal(4, x, 'Expected set to have 4 items')
    assert_raises(KeyError, my_set.insert_after, 3, 2)
    assert_raises(KeyError, my_set.insert_after, 5, 25)
    
  @test(depends_on=['test_append'])
  def test_has_element(self):
    """Test the has_element method of OrderedSet."""
    my_set = self.create_basic_set()
    assert_true(my_set.has_element(2))
    assert_false(my_set.has_element(4))
    

  @test(groups=['size_modifier'], depends_on=['test_append'])
  def test_remove(self):
    """Test the remove method of OrderedSet."""
    my_set = self.create_basic_set()
    my_set.remove(2)
    x = 0
    expected = [1, 3]
    for element in my_set:
      assert_equal(element, expected[x])
      x = x + 1
    assert_equal(2, x, 'Expected set to have 2 items')
    assert_raises(KeyError, my_set.remove, 2)
    
  @test(depends_on_groups=['size_modifier'])  
  def test_length(self):
    """Test the __length__ method of OrderedSet."""
    my_set = OrderedSet()
    assert_equal(len(my_set), 0)
    my_set.append(1)
    assert_equal(len(my_set), 1)
    my_set.prepend(2)
    assert_equal(len(my_set), 2)
    my_set.insert_after(1, 3)
    assert_equal(len(my_set), 3)
    my_set.remove(2)
    assert_equal(len(my_set), 2)    

@test
def test_iterator_to_list():
  """Test the iterator_to_list function."""
  my_set = OrderedSet()
  my_set.append(1)
  my_set.append(2)
  my_set.append(3)
  expected = [1, 2, 3]
  my_list = iterator_to_list(my_set)
  assert_equal(type(my_list), type(expected), 'Expected the result to be a list.')
  assert_equal(my_list, expected)
  
@test
def test_index_of_sorted_list():
  """Test the index_of_sorted_list function."""
  list = [1, 3, 5, 7, 9, 11]
  x = 5
  expected = 2
  assert_equal(index_of_sorted_list(x, list), expected)
  x = 4
  expected = -1
  assert_equal(index_of_sorted_list(x, list), expected)
   
if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()