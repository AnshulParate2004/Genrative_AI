from sympy import symbols, Eq, solve

x = symbols('x')
equation = Eq(2*x + 5, 15)
solution = solve(equation, x)

print(solution)  # [5]
