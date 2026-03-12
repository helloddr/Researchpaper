def add_numbers(a: float, b: float) -> float:
    return a + b


if __name__ == "__main__":
    first = float(input("Enter first number: "))
    second = float(input("Enter second number: "))
    print("Sum:", add_numbers(first, second))
