import sys
import msvcrt
import os
import time

# CONFIGURACIÓN
FILAS = 80
COLS  = 80

CELULA_VIVA   = "■"
CELULA_MUERTA = "·"
CURSOR_VIVA   = "▣"
CURSOR_MUERTA = "□"

COLORES_HEX = {
    "verde":    "39d353",
    "cyan":     "56d8e4",
    "amarillo": "f0e040",
    "blanco":   "c9d1d9",
    "gris":     "4a5568",
    "titulo":   "eda73b",
    "autor":    "0969da",
    "cursor":   "e43b44",
    "barra":    "8b9bb4",
}

# COMANDOS DE CONSOLA 
def cls_imprimir(texto):
    sys.stdout.write(texto)
    sys.stdout.flush()

def cls_mover_cursor(fila, columna):
    cls_imprimir(f"\033[{fila};{columna}H")

def cls_ocultar_cursor():
    cls_imprimir("\033[?25l")

def cls_mostrar_cursor():
    cls_imprimir("\033[?25h")

def cls_limpiar_pantalla():
    cls_imprimir("\033[2J\033[H")

def cls_restaurar_colores():
    cls_imprimir("\033[0m")

def cls_establecer_color_hex(hex_color):
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    cls_imprimir(f"\033[38;2;{r};{g};{b}m")

def cls_leer_tecla():
    if not msvcrt.kbhit():
        return None

    tecla = msvcrt.getch()

    if tecla == b'\r':
        return "ENTER"

    if tecla in (b'\x00', b'\xe0'):
        flecha = msvcrt.getch()
        if flecha == b'H': return "ARRIBA"
        if flecha == b'P': return "ABAJO"
        if flecha == b'M': return "DERECHA"
        if flecha == b'K': return "IZQUIERDA"

    if tecla.lower() == b'q' or tecla == b'\x1b':
        return "SALIR"

    if tecla == b' ':
        return "ESPACIO"

    return None

# LÓGICA DEL JUEGO DE LA VIDA
def crear_cuadricula():
    return [[False] * COLS for _ in range(FILAS)]

def contar_vecinos(cuadricula, f, c):
    total = 0
    for df in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if df == 0 and dc == 0:
                continue
            nf = (f + df) % FILAS
            nc = (c + dc) % COLS
            if cuadricula[nf][nc]:
                total += 1
    return total

def siguiente_generacion(cuadricula):
    nueva = crear_cuadricula()
    for f in range(FILAS):
        for c in range(COLS):
            vecinos = contar_vecinos(cuadricula, f, c)
            if cuadricula[f][c]:
                nueva[f][c] = vecinos in (2, 3)
            else:
                nueva[f][c] = vecinos == 3
    return nueva

# FUNCIONES DE DIBUJO
OFFSET_FILA = 5   
OFFSET_COL  = 2   

def dibujar_encabezado():
    lineas = [
        ("titulo", "============================================"),
        ("titulo", "|      El Juego de la Vida de Conway       |"),
        ("autor",  "|   Universidad de Sonora — Carlos S.V.    |"),
        ("titulo", "============================================"),
    ]
    for i, (color, texto) in enumerate(lineas, start=1):
        cls_mover_cursor(i, OFFSET_COL)
        cls_establecer_color_hex(COLORES_HEX[color])
        cls_imprimir(texto)
    cls_restaurar_colores()

def dibujar_barra_estado(generacion, vivas, simulando):
    modo  = " SIMULANDO " if simulando else " EDITANDO "
    barra = (
        f"  Gen:{generacion:>4}  Vivas:{vivas:>4}  {modo}  "
        f" | [ENTER] Iniciar/Pausa | [ESPACIO] Añadir Celula | [Q] Salir | "
    )
    cls_mover_cursor(OFFSET_FILA - 1, OFFSET_COL)
    cls_establecer_color_hex(COLORES_HEX["barra"])
    cls_imprimir(barra[:105])
    cls_restaurar_colores()

def dibujar_celula(f, c, viva, es_cursor):
    fila_pan = OFFSET_FILA + f
    col_pan  = OFFSET_COL  + c * 2   

    cls_mover_cursor(fila_pan, col_pan)

    if es_cursor:
        cls_establecer_color_hex(COLORES_HEX["cursor"])
        cls_imprimir(CURSOR_VIVA if viva else CURSOR_MUERTA)
    elif viva:
        cls_establecer_color_hex(COLORES_HEX["verde"])
        cls_imprimir(CELULA_VIVA)
    else:
        cls_establecer_color_hex(COLORES_HEX["gris"])
        cls_imprimir(CELULA_MUERTA)

    cls_restaurar_colores()

def dibujar_cuadricula_completa(cuadricula, cursor_f, cursor_c):
    for f in range(FILAS):
        for c in range(COLS):
            dibujar_celula(f, c, cuadricula[f][c], f == cursor_f and c == cursor_c)

def dibujar_generacion(cuadricula_vieja, cuadricula_nueva):
    for f in range(FILAS):
        for c in range(COLS):
            if cuadricula_vieja[f][c] != cuadricula_nueva[f][c]:
                dibujar_celula(f, c, cuadricula_nueva[f][c], False)

# PROGRAMA PRINCIPAL
def iniciar_juego():
    os.system("")          
    cls_ocultar_cursor()
    cls_limpiar_pantalla()

    cuadricula = crear_cuadricula()
    cursor_f   = FILAS // 2
    cursor_c   = COLS  // 2
    simulando  = False
    generacion = 0
    velocidad  = 0.1        

    dibujar_encabezado()
    dibujar_cuadricula_completa(cuadricula, cursor_f, cursor_c)
    dibujar_barra_estado(generacion, 0, simulando)

    try:
        while True:
            comando = cls_leer_tecla()

            if comando == "SALIR":
                break

            if not simulando:
                # Modo edición
                fila_ant, col_ant = cursor_f, cursor_c

                if comando == "ARRIBA":
                    cursor_f = max(0, cursor_f - 1)
                elif comando == "ABAJO":
                    cursor_f = min(FILAS - 1, cursor_f + 1)
                elif comando == "DERECHA":
                    cursor_c = min(COLS - 1, cursor_c + 1)
                elif comando == "IZQUIERDA":
                    cursor_c = max(0, cursor_c - 1)
                elif comando == "ESPACIO":     
                    cuadricula[cursor_f][cursor_c] = not cuadricula[cursor_f][cursor_c]
                    dibujar_celula(cursor_f, cursor_c, cuadricula[cursor_f][cursor_c], True)
                elif comando == "ENTER":
                    simulando = True
                    dibujar_cuadricula_completa(cuadricula, cursor_f, cursor_c)

                if cursor_f != fila_ant or cursor_c != col_ant:
                    dibujar_celula(fila_ant, col_ant, cuadricula[fila_ant][col_ant], False)
                    dibujar_celula(cursor_f,  cursor_c,  cuadricula[cursor_f][cursor_c],  True)

            else:
                # Modo simulación
                if comando == "ESPACIO" or comando == "ENTER":
                    simulando = False
                    dibujar_cuadricula_completa(cuadricula, cursor_f, cursor_c)
                else:
                    time.sleep(velocidad)
                    nueva = siguiente_generacion(cuadricula)
                    dibujar_generacion(cuadricula, nueva)
                    cuadricula = nueva
                    generacion += 1

            vivas = sum(cuadricula[f][c] for f in range(FILAS) for c in range(COLS))
            dibujar_barra_estado(generacion, vivas, simulando)

    finally:
        cls_restaurar_colores()
        cls_mostrar_cursor()
        cls_mover_cursor(OFFSET_FILA + FILAS + 2, 1)
        print("¡Hasta luego!")

if __name__ == "__main__":
    iniciar_juego()
