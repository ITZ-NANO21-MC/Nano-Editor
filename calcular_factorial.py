def calcular_factorial(numero):
    if not isinstance(numero, int):
        raise TypeError("El input debe ser un número entero.")
    if numero < 0:
        raise ValueError("El factorial no está definido para números negativos.")
    elif numero == 0:
        return 1
    else:
        factorial = 1
        for i in range(1, numero + 1):
            factorial *= i
        return factorial

if __name__ == "__main__":
    while True:
        try:
            num_str = input("Ingresa un número entero no negativo (o 'salir' para terminar): ")
            if num_str.lower() == 'salir':
                break
            
            num = int(num_str)
            
            resultado = calcular_factorial(num)
            print(f"El factorial de {num} es: {resultado}")
            
        except ValueError as e:
            print(f"Error: {e}. Por favor, ingresa un número entero no negativo válido.")
        except TypeError as e:
            print(f"Error inesperado de tipo: {e}.")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")