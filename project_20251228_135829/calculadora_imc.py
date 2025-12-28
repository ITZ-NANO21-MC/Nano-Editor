def calcular_imc(peso, altura):
    """Calcula el Índice de Masa Corporal (IMC).

    Args:
        peso (float): El peso de la persona en kilogramos.
        altura (float): La altura de la persona en metros.

    Returns:
        float: El valor del IMC.
    """
    if altura <= 0:
        raise ValueError("La altura debe ser un valor positivo.")
    return peso / (altura ** 2)

def interpretar_imc(imc):
    """Interpreta el valor del IMC y devuelve una categoría.

    Args:
        imc (float): El valor del IMC.

    Returns:
        str: La categoría del IMC.
    """
    if imc < 18.5:
        return "Bajo peso"
    elif 18.5 <= imc < 24.9:
        return "Peso normal"
    elif 25 <= imc < 29.9:
        return "Sobrepeso"
    else:
        return "Obesidad"

if __name__ == "__main__":
    try:
        peso_kg = float(input("Ingresa tu peso en kilogramos (ej: 70.5): "))
        altura_m = float(input("Ingresa tu altura en metros (ej: 1.75): "))

        imc_calculado = calcular_imc(peso_kg, altura_m)
        categoria = interpretar_imc(imc_calculado)

        print(f"\nTu IMC es: {imc_calculado:.2f}")
        print(f"Categoría: {categoria}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
