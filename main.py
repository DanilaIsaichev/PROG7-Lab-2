import concurrent.futures as ftres
import multiprocessing as mp
import timeit
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

  a_dec = Decimal(a)
  b_dec = Decimal(b)

  # Вычисление шага
  h = (b_dec - a_dec) / n_iter

  # Вычисление суммы значений функции от крайних значений промежутка
  s = f(a_dec) + f(b_dec)

  # Определяем наиболее оптимальное число потоков
  if cpu_u <= 2: 
    with ftres.ThreadPoolExecutor(max_workers=2) as executer:
      # Поток для первого цикла
      s1 = executer.submit(integrate_sum_dec, f, a_dec, b_dec - h, 2 * h)

      # Поток для второго цикла
      s2 = executer.submit(integrate_sum_dec, f, a_dec + 2 * h, b_dec - 2 * h, 2 * h)

    g = 4 * s1.result() + 2 * s2.result()

  elif cpu_u > 2 and cpu_u <= 4: 
    with ftres.ThreadPoolExecutor(max_workers=4) as executer:
      # Потоки для первого цикла
      s11 = executer.submit(integrate_sum_dec, f, a_dec, b_dec/2, 2 * h)

      s12 = executer.submit(integrate_sum_dec, f, b_dec/2 + 2 * h, b_dec - h, 2 * h)

      # Потоки для второго цикла
      s21 = executer.submit(integrate_sum_dec, f, a_dec + 2 * h, b_dec/2 - 2 * h, 2 * h)

      s22 = executer.submit(integrate_sum_dec, f, b_dec/2, b_dec - 2 * h, 2 * h)

    g = 4 * (s11.result() + s12.result()) + 2 * (s21.result() + s22.result())
  
  else:
    #TODO: проверить правильность вычислений
    with ftres.ThreadPoolExecutor(max_workers=6) as executer:
      # Потоки для первого цикла
      s11 = executer.submit(integrate_sum_dec, f, a_dec, b_dec/3, 2 * h)

      s12 = executer.submit(integrate_sum_dec, f, b_dec/3 + 2 * h, 2 * b_dec/3, 2 * h)

      s13 = executer.submit(integrate_sum_dec, f, 2 * b_dec/3 + 2 * h, b_dec - h, 2 * h)

      # Потоки для второго цикла
      s21 = executer.submit(integrate_sum_dec, f, a_dec + 2 * h, b_dec/3, 2 * h)

      s22 = executer.submit(integrate_sum_dec, f, b_dec/3 + 2 * h, 2 * b_dec/3, 2 * h)

      s23 = executer.submit(integrate_sum_dec, f, 2 * b_dec/3 + 2 * h, b_dec - 2 * h, 2 * h)

    g = 4 * (s11.result() + s12.result() + s13.result()) + 2 * (s21.result() + s22.result() + s23.result())


  return Decimal(h/(Decimal(3))) * Decimal(g + s)#format((h/3) * (g + s)), ".8f")


def integrate_sum(f, a: float, b: float, h: float) -> float:
    s = 0
    while a <= b:
        s += f(a)
        a += h
    return s


def integrate_sum_dec(f, a: Decimal, b: Decimal, h: Decimal) -> Decimal:
    s = Decimal(0)
    while a <= b:
        s += f(a)
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
