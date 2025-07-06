import sys
import random
import time
import tracemalloc
import os
import statistics

# Aumentar límite de recursión para DP recursivo
sys.setrecursionlimit(10000)

# Intentar importar colorama para salida en color
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR = True
except ImportError:
    class Dummy:
        RESET_ALL = ''
        RED = CYAN = WHITE = GREEN = MAGENTA = ''
    Fore = Style = Dummy
    COLOR = False

# Direcciones: arriba, abajo, izquierda, derecha
DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Símbolos para representaciones
SIMBOLOS = {
    'S': '🏁',  # Inicio
    'E': '🎯',  # Fin
    'B': '💣',  # Bomba
    'R': '🧪',  # RadAway
    '.': '🕳️',  # Hueco vacío
}
COLORES = {
    'S': Fore.GREEN,
    'E': Fore.MAGENTA,
    'B': Fore.RED,
    'R': Fore.CYAN,
    '.': Fore.WHITE,
}


def generar_cuadricula(n: int, prob_bomba: float = 0.2, prob_radaway: float = 0.2) -> list[list[str]]:
    """
    Genera una cuadrícula n×n con probabilidades de bomba y RadAway.
    Coloca 'S' en (0,0) e 'E' en (n-1,n-1).
    """
    cuadricula = []
    for i in range(n):
        fila = []
        for j in range(n):
            r = random.random()
            if r < prob_bomba:
                fila.append('B')
            elif r < prob_bomba + prob_radaway:
                fila.append('R')
            else:
                fila.append('.')
        cuadricula.append(fila)
    cuadricula[0][0] = 'S'
    cuadricula[-1][-1] = 'E'
    return cuadricula


def dp_recursivo_arreglo(cuadricula: list[list[str]]) -> tuple[int, int]:
    """
    DP recursivo (Top-Down) con arreglo 3D.
    Retorna (máx RadAway, estados explorados).
    """
    n = len(cuadricula)
    tmax = 2 * n - 1
    memo = [[[-1] * (tmax + 1) for _ in range(n)] for _ in range(n)]
    estados = 0

    def dfs(x: int, y: int, t: int) -> int:
        nonlocal estados
        estados += 1
        if not (0 <= x < n and 0 <= y < n) or cuadricula[x][y] == 'B' or t > tmax:
            return -10**9
        if cuadricula[x][y] == 'E':
            return 0
        if memo[x][y][t] != -1:
            return memo[x][y][t]
        mejor = max(dfs(x+dx, y+dy, t+1) for dx, dy in DIRECCIONES)
        ganancia = 1 if cuadricula[x][y] == 'R' else 0
        memo[x][y][t] = mejor + ganancia
        return memo[x][y][t]

    resultado = dfs(0, 0, 0)
    return max(0, resultado), estados


def dp_recursivo_diccionario(cuadricula: list[list[str]]) -> tuple[int, int]:
    """
    DP recursivo (Top-Down) con diccionario de memorización.
    Retorna (máx RadAway, estados explorados).
    """
    n = len(cuadricula)
    tmax = 2 * n - 1
    memo = {}
    estados = 0

    def dfs(x: int, y: int, t: int) -> int:
        nonlocal estados
        estados += 1
        if not (0 <= x < n and 0 <= y < n) or cuadricula[x][y] == 'B' or t > tmax:
            return -10**9
        if cuadricula[x][y] == 'E':
            return 0
        clave = (x, y, t)
        if clave in memo:
            return memo[clave]
        mejor = max(dfs(x+dx, y+dy, t+1) for dx, dy in DIRECCIONES)
        memo[clave] = mejor + (1 if cuadricula[x][y] == 'R' else 0)
        return memo[clave]

    resultado = dfs(0, 0, 0)
    return max(0, resultado), estados


def dp_abajo_arriba(cuadricula: list[list[str]]) -> tuple[int, int, list[tuple[int,int]]]:
    """
    DP iterativo (Bottom-Up) según esquema SRTBOT, con reconstrucción de ruta (Traceback).
    Retorna (máx RadAway, entradas en tabla, ruta óptima como lista de (x,y)).
    """
    n = len(cuadricula)
    tmax = 2 * n - 1
    dp = [[[0 if cuadricula[x][y] == 'E' else -10**9 for y in range(n)] for x in range(n)] for _ in range(tmax + 1)]
    for t in range(tmax - 1, -1, -1):
        for x in range(n):
            for y in range(n):
                if cuadricula[x][y] in ('B', 'E'):
                    continue
                mejor = max(dp[t+1][x+dx][y+dy] for dx, dy in DIRECCIONES if 0 <= x+dx < n and 0 <= y+dy < n)
                dp[t][x][y] = mejor + (1 if cuadricula[x][y] == 'R' else 0)
    resultado = max(0, dp[0][0][0])
    estados = (tmax + 1) * n * n

    ruta = [(0, 0)]
    x, y, t = 0, 0, 0
    while (x, y) != (len(cuadricula)-1, len(cuadricula)-1) and t < tmax:
        paso = dp[t][x][y] - (1 if cuadricula[x][y] == 'R' else 0)
        for dx, dy in DIRECCIONES:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(cuadricula) and 0 <= ny < len(cuadricula) and dp[t+1][nx][ny] == paso:
                x, y = nx, ny
                ruta.append((x, y))
                t += 1
                break

    return resultado, estados, ruta


def mostrar_cuadricula(cuadricula: list[list[str]]) -> None:
    """
    Imprime la cuadrícula con índices y leyenda.
    """
    n = len(cuadricula)
    print('   ' + ''.join(f'{j:3}' for j in range(n)))
    for i, fila in enumerate(cuadricula):
        linea = ''
        for celda in fila:
            sim = SIMBOLOS[celda]
            col = COLORES[celda] if COLOR else ''
            linea += f'{col}{sim}{Style.RESET_ALL} '.ljust(3)
        print(f'{i:2} ' + linea)
    leyenda = ', '.join(f"{SIMBOLOS[k]}={v}" for k, v in [
        ('S', 'Inicio'),
        ('E', 'Fin'),
        ('B', 'Bomba'),
        ('R', 'RadAway'),
        ('.', 'Hueco vacío')
    ])
    print(f"\nLeyenda: {leyenda}")


def comparativa_benchmark(cuadricula: list[list[str]], repeticiones: int = 3) -> None:
    """
    Ejecuta benchmark midiendo tiempo, estados y memoria.
    También muestra ruta para Bottom-Up.
    """
    print(f"Benchmark n={len(cuadricula)}")
    for nombre, func in [
        ('Arreglo', dp_recursivo_arreglo),
        ('Diccionario', dp_recursivo_diccionario),
        ('BottomUp', dp_abajo_arriba)
    ]:
        if nombre == 'BottomUp':
            resultado, estados, ruta = func(cuadricula)
        else:
            resultado, estados = func(cuadricula)

        tracemalloc.start()
        func(cuadricula)
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tiempos = []
        for _ in range(repeticiones):
            inicio = time.perf_counter()
            func(cuadricula)
            tiempos.append(time.perf_counter() - inicio)

        print(f"{nombre:<10}| RadAway={resultado:<3}| Estados={estados:<6}| "
              f"Tiempo={sum(tiempos)/repeticiones:.6f}s| Memoria pico={pico/1024:.2f}KiB")
        if nombre == 'BottomUp':
            print(f"Ruta óptima: {ruta}")
    print()


def comparativa_experimental(ns: list[int], instancias: int = 5, repeticiones: int = 3) -> None:
    """
    Automatiza Parte 3: para cada n genera instancias aleatorias, mide y promedia.
    """
    estrategias = [
        ('Arreglo', dp_recursivo_arreglo),
        ('Diccionario', dp_recursivo_diccionario),
        ('BottomUp', lambda g: dp_abajo_arriba(g)[:2])
    ]

    header = f"{'n':>4} | {'Estrategia':>12} | {'Rad':>3} | {'Estados':>8} | {'Tiempo(s)':>10} | {'Mem(KiB)':>9}"
    print(header)
    print('-' * len(header))
    for n in ns:
        acum = {nombre: {'rad': [], 'est': [], 't': [], 'm': []} for nombre, _ in estrategias}
        for _ in range(instancias):
            grid = generar_cuadricula(n)
            for nombre, func in estrategias:
                res, est = func(grid)
                tracemalloc.start()
                func(grid)
                _, pico = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                tiempos = []
                for _ in range(repeticiones):
                    t0 = time.perf_counter()
                    func(grid)
                    tiempos.append(time.perf_counter() - t0)
                acum[nombre]['rad'].append(res)
                acum[nombre]['est'].append(est)
                acum[nombre]['t'].append(statistics.mean(tiempos))
                acum[nombre]['m'].append(pico / 1024)
        for nombre in acum:
            datos = acum[nombre]
            print(f"{n:4d} | {nombre:12s} | "
                  f"{statistics.mean(datos['rad']):3.0f} | "
                  f"{statistics.mean(datos['est']):8.0f} | "
                  f"{statistics.mean(datos['t']):10.6f} | "
                  f"{statistics.mean(datos['m']):9.2f}")
    print()


def menu_principal() -> None:
    """
    Menú interactivo para configurar y ejecutar algoritmos.
    """
    tamaño = 10
    prob_bomba = 0.2
    prob_radaway = 0.2
    cuadricula = None
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('=== Fallout RadAway DP ===')
        print(f'Tamaño={tamaño}, Bomba%={prob_bomba*100:.0f}, RadAway%={prob_radaway*100:.0f}')
        print('1) Configurar parámetros')
        print('2) Generar cuadrícula')
        print('3) Mostrar cuadrícula')
        print('4) DP Arreglo (Top-Down)')       
        print('5) DP Diccionario (Top-Down)')
        print('6) DP Bottom-Up')
        print('7) Benchmark comparativo')
        print('8) Benchmark automático (n=10,20,30,40)')
        print('9) Salir')
        opcion = input('Elige [1-9]: ')
        if opcion == '1':
            try:
                tamaño = int(input('Ingresa tamaño: '))
                prob_bomba = float(input('Probabilidad de bomba [0-1]: '))
                prob_radaway = float(input('Probabilidad de RadAway [0-1]: '))
            except ValueError:
                print('Entrada inválida, manteniendo valores anteriores.')
                time.sleep(1)
        elif opcion == '2':
            cuadricula = generar_cuadricula(tamaño, prob_bomba, prob_radaway)
            print('Cuadrícula generada.')
            time.sleep(1)
        elif opcion == '3':
            if cuadricula:
                mostrar_cuadricula(cuadricula)
            else:
                print('Primero genera la cuadrícula.')
            input('Enter para continuar...')
        elif opcion == '4':
            if cuadricula:
                res, est = dp_recursivo_arreglo(cuadricula)
                print(f'DP Arreglo → RadAway={res}, Estados={est}')
            else:
                print('Primero genera la cuadrícula.')
            input('Enter para continuar...')
        elif opcion == '5':
            if cuadricula:
                res, est = dp_recursivo_diccionario(cuadricula)
                print(f'DP Diccionario → RadAway={res}, Estados={est}')
            else:
                print('Primero genera la cuadrícula.')
            input('Enter para continuar...')
        elif opcion == '6':
            if cuadricula:
                res, est, ruta = dp_abajo_arriba(cuadricula)
                print(f'DP Bottom-Up → RadAway={res}, Estados={est}')
                print(f'Ruta óptima: {ruta}')
            else:
                print('Primero genera la cuadrícula.')
            input('Enter para continuar...')
        elif opcion == '7':
            if cuadricula:
                comparativa_benchmark(cuadricula)
            else:
                print('Primero genera la cuadrícula.')
            input('Enter para continuar...')
        elif opcion == '8':
            comparativa_experimental([10, 20, 30, 40])
            input('Enter para continuar...')
        elif opcion == '9':
            break
        else:
            print('Opción no válida.')
            time.sleep(1)

if __name__ == '__main__':
    random.seed(0)
    menu_principal()
