import multiprocessing as mp
from decimal import *
from math import pi, sin


def simple_integrate(f, a: float, b: float, *, n_iter: int=1000) -> float:
  """Простое вычисление определённого интеграла методом парабол"""

  if b <= a:
    raise ValueError

  # Вычисление шага
  h = (b - a) / n_iter

  # Вычисление суммы значений функции от крайних значений промежутка
  s = f(a) + f(b)

  s1 = integrate_sum(f, a, b - h, 2 * h)

  s2 = integrate_sum(f, a + 2 * h, b - 2 * h, 2 * h)
  
  g = 4 * s1 + 2 * s2

  return format(h/3 * (g + s), ".8f")


def integrate_async(f, a: float, b: float, *, n_iter: int=1000, cpu_u=mp.cpu_count()) -> Decimal:
  """Оптимизированное вычисление определённого интеграла методом парабол"""

  getcontext().prec = 8

  if b <= a:
    raise ValueError

  # Переводим границы в Decimal
  a_dec = Decimal(a)
  b_dec = Decimal(b)

  # Вычисление шага
  h = (b_dec - a_dec) / n_iter

  # Вычисление суммы значений функции от крайних значений промежутка с пееводом в Decimal
  s = Decimal(f(a_dec)) + Decimal(f(b_dec))

  # Определяем наиболее оптимальное число потоков
  if cpu_u <= 2: 
    with mp.Pool(2) as p:
      # starmap - метод, позволяющий передавать функции наборы аргументов
      result = p.starmap(integrate_sum_dec, [
        (f, a_dec, b_dec - h, 2 * h),
        (f, a_dec + 2 * h, b_dec - 2 * h, 2 * h)
      ])

    g = 4 * result[0] + 2 * result[1]

  elif cpu_u > 2 and cpu_u <= 4: 
    with mp.Pool(4) as p:
      # starmap - метод, позволяющий передавать функции наборы аргументов
      result = p.starmap(integrate_sum_dec, [
        (f, a_dec, b_dec/2, 2 * h),
        (f, b_dec/2 + 2 * h, b_dec - h, 2 * h),
        (f, a_dec + 2 * h, b_dec/2 - 2 * h, 2 * h),
        (f, b_dec/2, b_dec - 2 * h, 2 * h)
      ])

    g = 4 * (result[0] + result[1]) + 2 * (result[2] + result[3])
  
  else:
    #TODO: проверить правильность вычислений
    with mp.Pool(6) as p:
      # starmap - метод, позволяющий передавать функции наборы аргументов
      result = p.starmap(integrate_sum_dec, [
        (f, a_dec, b_dec/3, 2 * h),
        (f, b_dec/3 + 2 * h, 2 * b_dec/3, 2 * h),
        (f, 2 * b_dec/3 + 2 * h, b_dec - h, 2 * h),
        (f, a_dec + 2 * h, b_dec/3, 2 * h),
        (f, b_dec/3 + 2 * h, 2 * b_dec/3, 2 * h),
        (f, 2 * b_dec/3 + 2 * h, b_dec - 2 * h, 2 * h)
      ])

    g = 4 * (result[0] + result[1] + result[2]) + 2 * (result[3] + result[4] + result[5])

  return Decimal(h/(Decimal(3))) * Decimal(g + s)


def integrate_sum(f, a: float, b: float, h: float) -> float:
  s = 0
  while a <= b:
    s += f(a)
    a += h
  return s


def integrate_sum_dec(f, a: Decimal, b: Decimal, h: Decimal) -> Decimal:
  s = Decimal(0)
  while a <= b:
    s += Decimal(f(a))
    a += h
  return s


def my_function(x: float) -> float:
  return (2 * x * x + 0.7) ** (1 / 2) / (1.5 + (0.8 * x + 1) ** (1 / 2))


def my_function_dec(x: Decimal) -> Decimal:
  return (Decimal(2) * Decimal(x) * Decimal(x) + Decimal(0.7)) ** Decimal(1 / 2) / (Decimal(1.5) + (Decimal(0.8) * Decimal(x) + Decimal(1)) ** Decimal(1 / 2))



if __name__ == '__main__':

  print("---==Custom function==---")
  # python -m timeit -s "from main import simple_integrate, my_function; simple_integrate(my_function, 1.2, 3, n_iter=100000)" -r 100 -u msec 
  print("Result:", simple_integrate(my_function, 1.2, 3, n_iter=100000))
  # python -m timeit -s "from main import integrate_async, my_function_dec; integrate_async(my_function_dec, 1.2, 3, n_iter=100000, cpu_u=2)" -r 100 -u msec 
  print("Async result (2):", integrate_async(my_function_dec, 1.2, 3, n_iter=100000, cpu_u=2))
  # python -m timeit -s "from main import integrate_async, my_function_dec; integrate_async(my_function_dec, 1.2, 3, n_iter=100000, cpu_u=4)" -r 100 -u msec 
  print("Async result (4):", integrate_async(my_function_dec, 1.2, 3, n_iter=100000, cpu_u=4))
  # python -m timeit -s "from main import integrate_async, my_function_dec; integrate_async(my_function_dec, 1.2, 3, n_iter=100000, cpu_u=6)" -r 100 -u msec 
  print("Async result (6):", integrate_async(my_function_dec, 1.2, 3, n_iter=100000, cpu_u=6))

  print("\n---==sin(x)==---")
  # python -m timeit -s "from main import simple_integrate; from math import sin, pi; simple_integrate(sin, 0, pi/2)" -r 100 -u msec 
  print("Result:", simple_integrate(sin, 0, pi/2, n_iter=100000))
  # python -m timeit -s "from main import integrate_async; from math import sin, pi; integrate_async(sin, 0, pi/2, cpu_u=2)" -r 100 -u msec 
  print("Async result (2):", integrate_async(sin, 0, pi/2, n_iter=100000, cpu_u=2))
  # python -m timeit -s "from main import integrate_async; from math import sin, pi; integrate_async(sin, 0, pi/2, cpu_u=4)" -r 100 -u msec 
  print("Async result (4):", integrate_async(sin, 0, pi/2, n_iter=100000, cpu_u=4))
  # python -m timeit -s "from main import integrate_async; from math import sin, pi; integrate_async(sin, 0, pi/2, cpu_u=6)" -r 100 -u msec 
  print("Async result (6):", integrate_async(sin, 0, pi/2, n_iter=100000, cpu_u=6))
