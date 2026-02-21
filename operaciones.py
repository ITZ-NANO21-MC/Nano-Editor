#!/usr/bin/env python3
def main():
    while True:
        print("Seleccione operación:")
        print("1. Suma")
        print("2. Resta")
        print("3. Multiplicación")
        print("4. División")
        print("5. Salir")

        choice = input("Ingrese su elección (1/2/3/4/5): ")

        if choice in ('1', '2', '3', '4'):
            try:
                num1 = float(input("Ingrese el primer número: "))
                num2 = float(input("Ingrese el segundo número: "))
            except ValueError:
                print("Entrada inválida. Por favor ingrese números.")
                continue

            if choice == '1':
                print(f"{num1} + {num2} = {suma(num1, num2)}")
            elif choice == '2':
                print(f"{num1} - {num2} = {resta(num1, num2)}")
            elif choice == '3':
                print(f"{num1} * {num2} = {multiplicacion(num1, num2)}")
            elif choice == '4':
                result = division(num1, num2)
                if isinstance(result, str):
                    print(result)
                else:
                    print(f"{num1} / {num2} = {result}")
        elif choice == '5':
            print("Saliendo de la calculadora.")
            break
        else:
            print("Opción inválida. Por favor intente de nuevo.")

def suma(a, b):
   return a + b

def resta(a, b):
  return a - b

def multiplicacion(a, b):
  return a * b

def division(a, b):
  if b == 0:
    return "Error: No se puede dividir por cero."
  return a / b

if __name__ == "__main__":
    main()
