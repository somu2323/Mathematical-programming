from scipy.optimize import linprog

def solve_simplex(obj, constraints, rhs):
    result = linprog(
        c=obj, 
        A_ub=constraints, 
        b_ub=rhs, 
        method="highs"
    )

    if result.success:
        return {
            "status": "Optimal",
            "x": result.x[0],
            "y": result.x[1],
            "objective_value": abs(result.fun)  # Ensures positive value
        }
    else:
        return {"status": "No Solution"}
