from scipy.optimize import linprog
import optype.numpy as onp


def main():
    print("Hello from facty!")

    # initial example from https://realpython.com/linear-programming-python/

    # minimize -z = -x - 2y
    obj = [-1, -2]

    # subject to:
    #  2x +  y <= 20
    # -4x + 5y <= 10
    #   x - 2y <= 2
    lhs_ineq: onp.ToFloat2D = [[2, 1], [-4, 5], [1, -2]]
    rhs_ineq: onp.ToFloat1D = [20, 10, 2]

    # and -x + 5y = 15
    lhs_eq: onp.ToFloat2D = [[-1, 5]]
    rhs_eq: onp.ToFloat1D = [15]

    # also x >= 0, y >= 0
    # TODO: does scipy-stubs have the wrong type here? it seems to only expect a single bound
    # rather than allowing a sequence
    bound = (0, None)

    result = linprog(
        c=obj,
        A_ub=lhs_ineq,
        b_ub=rhs_ineq,
        A_eq=lhs_eq,
        b_eq=rhs_eq,
        bounds=bound,
    )

    print(repr(result))


if __name__ == "__main__":
    main()
