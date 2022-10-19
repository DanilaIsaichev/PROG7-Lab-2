import unittest

from main import (integrate_async, my_function, my_function_dec,
                  simple_integrate)


class TestStringMethods(unittest.TestCase):

  # Тесты для 2 потоков
  def test_precision_u2_1(self):
    self.assertAlmostEqual(float(integrate_async(my_function_dec, 1.2, 3, cpu_u=2)), float(simple_integrate(my_function, 1.2, 3)), delta=0.01)


  def test_precision_u2_2(self):
    self.assertAlmostEqual(float(integrate_async(my_function_dec, 1.2, 3, n_iter=10000, cpu_u=2)), float(simple_integrate(my_function, 1.2, 3, n_iter=10000)), delta=0.001)


  # Тесты для 4 потоков
  def test_precision_u4_1(self):
    self.assertAlmostEqual(float(integrate_async(my_function_dec, 1.2, 3, cpu_u=4)), float(simple_integrate(my_function, 1.2, 3)), delta=0.01)


  def test_precision_u4_2(self):
    self.assertAlmostEqual(float(integrate_async(my_function_dec, 1.2, 3, n_iter=10000, cpu_u=4)), float(simple_integrate(my_function, 1.2, 3, n_iter=10000)), delta=0.001)


  # Тесты для 6 потоков
  def test_precision_u6_1(self):
    self.assertAlmostEqual(float(integrate_async(my_function_dec, 1.2, 3, cpu_u=6)), float(simple_integrate(my_function, 1.2, 3)), delta=0.01)


  def test_precision_u6_2(self):
    self.assertAlmostEqual(float(integrate_async(my_function_dec, 1.2, 3, n_iter=10000, cpu_u=66)), float(simple_integrate(my_function, 1.2, 3, n_iter=10000)), delta=0.001)


  def test_zero_1(self):
    with self.assertRaises(ValueError):
      simple_integrate(lambda x: x + 1, 0, 0)


  def test_zero_2(self):
    with self.assertRaises(ValueError):
      integrate_async(lambda x: x + 1, 0, 0)


if __name__ == '__main__':
    unittest.main()
