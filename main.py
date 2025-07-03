import random
import time
import os

# Intentar importar colorama para colores en consola
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Definir alias y estilo por defecto
    class DummyStyle:
        RESET_ALL = ''
    class DummyFore:
        RED = ''
        CYAN = ''
        WHITE = ''
        GREEN = ''
        MAGENTA = ''
    Style = DummyStyle
    Fore = DummyFore
    COLORAMA_AVAILABLE = False

# Movimientos: arriba, abajo, izquierda, derecha
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Símbolos y colores para impresión
SYMBOLS = {
    'B': '💣',  # Bomba
    'R': '🧪',  # RadAway
    '.': '🕳️',   # Vacío
    'S': '🏁',  # Inicio
    'E': '🎯'   # Final
}
COLORS = {
    'B': Fore.RED,
    'R': Fore.CYAN,
    '.': Fore.WHITE,
    'S': Fore.GREEN,
    'E': Fore.MAGENTA
}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_grid(n: int, bomb_prob: float = 0.2, radaway_prob: float = 0.2) -> list:
    """
    Genera cuadrícula n×n con bombas ('B'), RadAway ('R') y vacíos ('.').
    Posición inicial marcada 'S', final 'E'.
    """
    grid = []
    for i in range(n):
        row = []
        for j in range(n):
            r = random.random()
            if r < bomb_prob:
                row.append('B')
            elif r < bomb_prob + radaway_prob:
                row.append('R')
            else:
                row.append('.')
        grid.append(row)
    grid[0][0] = 'S'
    grid[n-1][n-1] = 'E'
    return grid


def dp_array_max_radaway(grid: list) -> tuple:
    """
    Memorización con arreglo 3D. Devuelve (max_radaways, estados_explorados).
    """
    n = len(grid)
    tmax = 2 * n - 1
    dp = [[[-1]*(tmax+1) for _ in range(n)] for _ in range(n)]
    states = 0

    def f(x: int, y: int, t: int) -> int:
        nonlocal states
        states += 1
        if not (0 <= x < n and 0 <= y < n):
            return float('-inf')
        cell = grid[x][y]
        if cell == 'B' or t > tmax:
            return float('-inf')
        if cell == 'E':
            return 0
        if dp[x][y][t] != -1:
            return dp[x][y][t]
        best = float('-inf')
        for dx, dy in DIRS:
            best = max(best, f(x+dx, y+dy, t+1))
        gain = 1 if cell == 'R' else 0
        dp[x][y][t] = best + gain if best != float('-inf') else float('-inf')
        return dp[x][y][t]

    result = f(0, 0, 0)
    return (0 if result < 0 else result, states)


def dp_dict_max_radaway(grid: list) -> tuple:
    """
    Memorización con diccionario. Devuelve (max_radaways, estados_explorados).
    """
    n = len(grid)
    tmax = 2 * n - 1
    memo = {}
    states = 0

    def f(x: int, y: int, t: int) -> int:
        nonlocal states
        states += 1
        if not (0 <= x < n and 0 <= y < n):
            return float('-inf')
        cell = grid[x][y]
        if cell == 'B' or t > tmax:
            return float('-inf')
        if cell == 'E':
            return 0
        key = (x, y, t)
        if key in memo:
            return memo[key]
        best = float('-inf')
        for dx, dy in DIRS:
            best = max(best, f(x+dx, y+dy, t+1))
        gain = 1 if cell == 'R' else 0
        memo[key] = best + gain if best != float('-inf') else float('-inf')
        return memo[key]

    result = f(0, 0, 0)
    return (0 if result < 0 else result, states)


def display_grid(grid: list) -> None:
    """
    Imprime la cuadrícula con emojis, colores y leyenda.
    """
    n = len(grid)
    # Índices de columnas
    print('   ' + ' '.join(f'{j:2}' for j in range(n)))
    # Filas
    for i, row in enumerate(grid):
        line = ''
        for cell in row:
            symbol = SYMBOLS[cell]
            color = COLORS.get(cell, '')
            line += f'{color}{symbol}{Style.RESET_ALL} '
        print(f'{i:2} {line}')
    # Leyenda
    print('\nLeyenda:')
    for key, name in [('S', 'Inicio'), ('E', 'Final'), ('B', 'Bomba'), ('R', 'RadAway'), ('.', 'Vacío')]:
        print(f' {COLORS.get(key, "")}{SYMBOLS[key]}{Style.RESET_ALL} : {name}')
    print()


def benchmark(grid: list) -> None:
    """
    Muestra cápsulas, estados y tiempos de ambas estrategias.
    """
    print('\nComparativa de rendimiento:')
    for name, func in [('Arreglo 3D', dp_array_max_radaway), ('Diccionario', dp_dict_max_radaway)]:
        start = time.perf_counter()
        cap, states = func(grid)
        elapsed = time.perf_counter() - start
        print(f'{name:<12} | cápsulas={cap:<3} | estados={states:<6} | tiempo={elapsed:.6f}s')
    print()


def main_menu() -> None:
    grid = None
    bomb_prob = 0.2
    radaway_prob = 0.2
    while True:
        clear_screen()
        print('=== Fallout RadAway DP ===')
        print(f'Probabilidades → Bomba: {bomb_prob*100:.0f}%, RadAway: {radaway_prob*100:.0f}%')
        print('1. Configurar probabilidades')
        print('2. Generar cuadrícula')
        print('3. Mostrar cuadrícula')
        print('4. DP Arreglo 3D')
        print('5. DP Diccionario')
        print('6. Comparativa de rendimiento')
        print('7. Salir')
        choice = input('Elija opción (1-7): ')
        if choice == '1':
            try:
                bp = float(input('Prob bomba [0-1]: '))
                rp = float(input('Prob RadAway [0-1]: '))
                if 0 <= bp <= 1 and 0 <= rp <= 1:
                    bomb_prob, radaway_prob = bp, rp
                else:
                    raise ValueError
            except ValueError:
                print('Probabilidades inválidas. Se mantienen anteriores.')
                time.sleep(1)
        elif choice == '2':
            try:
                n = int(input('Tamaño cuadrícula: '))
                grid = generate_grid(n, bomb_prob, radaway_prob)
            except ValueError:
                print('Tamaño inválido.')
                time.sleep(1)
        elif choice == '3':
            if grid:
                display_grid(grid)
                input('Presione Enter para continuar...')
            else:
                print('Genere la cuadrícula primero.')
                time.sleep(1)
        elif choice == '4':
            if grid:
                cap, states = dp_array_max_radaway(grid)
                print(f'Arreglo 3D → cápsulas={cap}, estados={states}')
                input('Enter para continuar...')
            else:
                print('Genere la cuadrícula primero.')
                time.sleep(1)
        elif choice == '5':
            if grid:
                cap, states = dp_dict_max_radaway(grid)
                print(f'Diccionario → cápsulas={cap}, estados={states}')
                input('Enter para continuar...')
            else:
                print('Genere la cuadrícula primero.')
                time.sleep(1)
        elif choice == '6':
            if grid:
                benchmark(grid)
                input('Enter para continuar...')
            else:
                print('Genere la cuadrícula primero.')
                time.sleep(1)
        elif choice == '7':
            print('¡Hasta luego!')
            break
        else:
            print('Opción inválida.')
            time.sleep(1)


if __name__ == '__main__':
    random.seed(0)
    main_menu()