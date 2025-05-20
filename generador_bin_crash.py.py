import random
from datetime import datetime
import traceback # Para detalles de error

# -----------------------------------------------------------------------------
# Funciones de Lógica del Generador
# -----------------------------------------------------------------------------

def calcular_luhn_checksum(card_number_prefix):
    """Calcula el dígito de control de Luhn para un prefijo de número de tarjeta."""
    digits = [int(d) for d in card_number_prefix]
    for i in range(len(digits) - 1, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    total = sum(digits)
    checksum = (total * 9) % 10
    return checksum

def generar_numero_tarjeta_luhn(bin_code, total_card_length=16):
    """
    Genera un número de tarjeta con un BIN y checksum de Luhn.
    Asegura que el número de tarjeta completo (BIN + random + checksum)
    tenga la longitud total_card_length (por defecto 16).
    """
    bin_len = len(bin_code)
    num_random_digits_needed = total_card_length - bin_len - 1 # -1 para el checksum

    if num_random_digits_needed < 0:
        raise ValueError(f"La longitud del BIN ({bin_len}) es demasiado larga para la longitud total de la tarjeta ({total_card_length}).")

    random_digits = "".join([str(random.randint(0, 9)) for _ in range(num_random_digits_needed)])
    prefix_to_luhn_check = bin_code + random_digits
    
    checksum = calcular_luhn_checksum(prefix_to_luhn_check)
    # El número completo será el prefijo usado para Luhn + el checksum
    return prefix_to_luhn_check + str(checksum)

# -----------------------------------------------------------------------------
# Lógica de Generación de Datos
# -----------------------------------------------------------------------------

def generar_datos_tarjeta(bin_code, cantidad=1, mes_usuario=None, anio_usuario=None, anios_futuros_max_config=10):
    """
    Genera una lista de cadenas con formato de datos de tarjeta.
    Formato: NNN...XXX|MM|YY|CVV (Total 16 dígitos para NNN...XXX)
    """
    # Asume que bin_code ya ha sido validado (empieza con '4' para Visa, longitud correcta)
    resultados = []
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    for _ in range(cantidad):
        numero_tarjeta_completo = generar_numero_tarjeta_luhn(bin_code) # Genera 16 dígitos

        # --- Determinar Año de Expiración ---
        exp_year_full = current_year 
        if anio_usuario is not None: 
            if current_year <= anio_usuario <= current_year + anios_futuros_max_config:
                exp_year_full = anio_usuario
            else:
                print(f"  (!) Advertencia: Año '{anio_usuario}' inválido o fuera del rango ({current_year}-{current_year + anios_futuros_max_config}). Se usará uno aleatorio.")
                exp_year_full = random.randint(current_year, current_year + anios_futuros_max_config)
        else: 
            exp_year_full = random.randint(current_year, current_year + anios_futuros_max_config)

        # --- Determinar Mes de Expiración ---
        exp_month = current_month 
        if mes_usuario is not None: 
            if 1 <= mes_usuario <= 12:
                exp_month = mes_usuario
            else:
                print(f"  (!) Advertencia: Mes '{mes_usuario}' inválido. Se usará uno aleatorio.")
                if exp_year_full == current_year:
                    exp_month = random.randint(current_month, 12)
                else: 
                    exp_month = random.randint(1, 12)
        else: 
            if exp_year_full == current_year:
                exp_month = random.randint(current_month, 12)
            else: 
                exp_month = random.randint(1, 12)
        
        # --- Ajuste Final de Coherencia de Fecha ---
        if exp_year_full == current_year and exp_month < current_month:
            print(f"  (!) Ajuste: Mes {exp_month:02d} es pasado para el año {exp_year_full}. Se usará un mes válido.")
            exp_month = random.randint(current_month, 12)

        if exp_year_full < current_year or \
           (exp_year_full == current_year and exp_month < current_month):
            print(f"  (!) [Corrección Final]: La fecha calculada ({exp_month:02d}/{exp_year_full}) era pasada. Ajustando.")
            exp_year_full = current_year
            exp_month = random.randint(current_month, 12)

        mes_exp_str = f"{exp_month:02d}"
        anio_exp_str = f"{exp_year_full % 100:02d}"

        cvv = "".join([str(random.randint(0, 9)) for _ in range(3)])
        resultados.append(f"{numero_tarjeta_completo}|{mes_exp_str}|{anio_exp_str}|{cvv}")
        
    return resultados

# -----------------------------------------------------------------------------
# Interfaz de Usuario y Presentación
# -----------------------------------------------------------------------------

def display_header():
    """Muestra el encabezado de la aplicación con logo, eslogan y advertencia."""
    padlock_logo = [
        "        .--\"\"--.     ",
        "       /        \\    ",
        "      |  .--.  |  \\\\ ",
        "      |  |  |  |   ))",
        "       \\  `--'  //   ",
        "        `------'      ",
        "                        "
    ]
    slogan = "                   BIN-CRASH"
    warning_title = "          *** ADVERTENCIA MUY IMPORTANTE ***"
    warning_lines = [
        "===============================================================================",
        " Este programa genera números con formato de tarjeta y datos asociados",
        " SOLAMENTE con fines educativos, de prueba de software y para entender algoritmos.",
        "-------------------------------------------------------------------------------",
        "  -> NO UTILICES estos datos para intentos de compra o actividades fraudulentas.",
        "  -> Los números generados son FALSOS y NO CORRESPONDEN a tarjetas reales.",
        "  -> Cualquier uso indebido de esta herramienta es TU ÚNICA RESPONSABILIDAD.",
        "===============================================================================",
        "          ¡Usa esta herramienta de forma ética y responsable!",
        "-------------------------------------------------------------------------------"
    ]
    print("\n")
    for line in padlock_logo:
        print(line)
    print(slogan)
    print("\n") 
    print(warning_title)
    for line in warning_lines:
        print(line)
    print("\n")

if __name__ == "__main__":
    display_header()
    
    # --- PASO 1: Solicitar BIN de VISA (6 a 8 dígitos, debe empezar con '4') ---
    while True:
        input_bin = input("PASO 1: Introduce el código BIN de VISA (6-8 dígitos, debe empezar con '4'): ")
        bin_len = len(input_bin)
        if (6 <= bin_len <= 8) and input_bin.isdigit() and input_bin.startswith('4'):
            break
        else:
            if not input_bin.startswith('4'):
                print("  (!) Error: El BIN para VISA debe comenzar con el dígito '4'.")
            elif not (6 <= bin_len <= 8):
                print("  (!) Error: El BIN debe contener entre 6 y 8 números.")
            else: # No es numérico u otro error
                print("  (!) Error: El BIN debe ser numérico, de 6 a 8 dígitos y empezar con '4'.")
            print("      Intenta de nuevo.")


    print("--- Configuración de Fecha de Expiración (Opcional) ---")
    # --- PASO 2: Solicitar Mes (opcional) ---
    mes_usr = None
    while True:
        try:
            mes_str = input("PASO 2: Introduce el MES de expiración (1-12) o deja vacío para aleatorio: ")
            if not mes_str: 
                mes_usr = None
                break
            mes_usr = int(mes_str)
            if not (1 <= mes_usr <= 12):
                print("    (!) Error: Mes inválido. Debe ser entre 1 y 12.")
                mes_usr = None 
                continue 
            break 
        except ValueError:
            print("    (!) Error: Entrada inválida. Si introduces un valor, debe ser un número.")
    
    # --- PASO 3: Solicitar Año (opcional) ---
    anio_usr = None
    ANIOS_FUTUROS_MAX_CONFIG = 10 # Para validación de entrada y generación aleatoria
    while True:
        try:
            anio_str = input(f"PASO 3: Introduce el AÑO completo (ej: {datetime.now().year}, hasta {datetime.now().year + ANIOS_FUTUROS_MAX_CONFIG}) o deja vacío para aleatorio: ")
            if not anio_str: 
                anio_usr = None
                break
            anio_usr = int(anio_str)
            if not (datetime.now().year <= anio_usr <= datetime.now().year + ANIOS_FUTUROS_MAX_CONFIG): 
                print(f"    (!) Error: Año inválido o fuera del rango sugerido ({datetime.now().year} - {datetime.now().year + ANIOS_FUTUROS_MAX_CONFIG}).")
                anio_usr = None 
                continue 
            break
        except ValueError:
            print("    (!) Error: Entrada inválida. Si introduces un valor, debe ser un número.")
    
    print("PASO 4: El código CVV se generará aleatoriamente (3 dígitos).")

    # --- PASO 5: Solicitar Cantidad a generar ---
    while True:
        try:
            cantidad_a_generar = int(input("PASO 5: ¿Cuántos conjuntos de datos quieres generar?: "))
            if cantidad_a_generar > 0:
                break
            else:
                print("  (!) Error: Por favor, introduce un número mayor a 0.")
        except ValueError:
            print("  (!) Error: Entrada inválida. Por favor, introduce un número entero.")
    
    print("\nGenerando datos (exclusivamente formato VISA)...\n")
    
    try:
        datos_generados = generar_datos_tarjeta(
            input_bin, 
            cantidad_a_generar, 
            mes_usuario=mes_usr, 
            anio_usuario=anio_usr,
            anios_futuros_max_config=ANIOS_FUTUROS_MAX_CONFIG 
        )
        
        if datos_generados:
            print("Resultados generados:")
            print("------------------------------------------------------")
            for i, dato in enumerate(datos_generados):
                print(f"  {i+1}. {dato}")
            print("------------------------------------------------------")
        else:
            print("No se generaron datos. Verifica las entradas y la lógica interna si esto persiste.")
            
    except Exception as e:
        print(f"  (!) Error Crítico Inesperado durante la generación: {e}")
        print("  (!) Detalles del error:")
        traceback.print_exc()

    print("\n--- Fin del programa ---")