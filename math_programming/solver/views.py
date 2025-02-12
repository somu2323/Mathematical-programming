from django.shortcuts import render
from django.http import HttpResponseRedirect
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json
from .simplex_solver import solve_simplex

def home(request):
    if request.method == "POST":
        method = request.POST.get('method')
        objective_type = request.POST.get('objective')
        obj_x1 = request.POST.get('obj_x1')
        obj_x2 = request.POST.get('obj_x2')

        # Extract constraints
        constraints_json = request.POST.get('constraints', '[]')
        constraints_data = json.loads(constraints_json)

        constraints = []
        rhs = []
        for constraint in constraints_data:
            constraints.append([float(constraint['x1']), float(constraint['x2'])])
            rhs.append(float(constraint['rhs']))

        # Convert constraints to JSON string for passing in URL
        constraints_str = json.dumps(constraints)
        rhs_str = json.dumps(rhs)

        # Construct query parameters
        params = f"?objective={objective_type}&obj_x1={obj_x1}&obj_x2={obj_x2}&constraints={constraints_str}&rhs={rhs_str}"

        if method == 'simplex':
            return HttpResponseRedirect(f"/simplex/{params}")
        elif method == 'graphical':
            return HttpResponseRedirect(f"/graphical/{params}")

    return render(request, "solver/home.html")

def simplex_method(request):
    if request.method == "GET":
        objective_type = request.GET.get('objective')
        obj_x1 = float(request.GET.get('obj_x1'))
        obj_x2 = float(request.GET.get('obj_x2'))
        constraints = json.loads(request.GET.get('constraints', '[]'))
        rhs = json.loads(request.GET.get('rhs', '[]'))

        # Solve using Simplex method
        result = solve_simplex([-obj_x1, -obj_x2] if objective_type == 'max' else [obj_x1, obj_x2], constraints, rhs)
        return render(request, "solver/result.html", {"result": result})

    return render(request, "solver/home.html")

def graphical_method(request):
    if request.method == "GET":
        objective_type = request.GET.get('objective')
        obj_x1 = float(request.GET.get('obj_x1'))
        obj_x2 = float(request.GET.get('obj_x2'))
        constraints = json.loads(request.GET.get('constraints', '[]'))
        rhs = json.loads(request.GET.get('rhs', '[]'))

        # Generate graph and get optimal solution
        graph_image, optimal_point, optimal_value = plot_graphical(constraints, rhs, objective_type, obj_x1, obj_x2)

        # Ensure optimal_point is a tuple (x1, x2)
        if optimal_point is not None:
            optimal_point = tuple(optimal_point)  # Convert to tuple if necessary

        return render(request, "solver/graphical_result.html", {
            "graph_image": graph_image,
            "optimal_point": optimal_point,
            "optimal_value": optimal_value
        })

    return render(request, "solver/home.html")

def plot_graphical(constraints, rhs, objective, obj_x1, obj_x2):
    x1_vals = np.linspace(0, 20, 500)  # Extended range for better scaling
    feasible_x1 = []
    feasible_x2 = []

    plt.figure(figsize=(8, 8))

    for i in range(len(constraints)):
        if constraints[i][1] != 0:  # Normal constraint
            x2_constraint = (rhs[i] - constraints[i][0] * x1_vals) / constraints[i][1]
            plt.plot(x1_vals, x2_constraint, label=f'Constraint {i+1}')
        else:
            # Vertical constraint line (x1 = c)
            x_val = rhs[i] / constraints[i][0]
            plt.axvline(x=x_val, linestyle="--", color="red", label=f'Constraint {i+1}')

    # Find intersection points (feasible region boundary)
    feasible_region_x = []
    feasible_region_y = []
    optimal_point = None
    optimal_value = None
    for i in range(len(constraints)):
        for j in range(i + 1, len(constraints)):
            A = np.array([constraints[i], constraints[j]])
            b = np.array([rhs[i], rhs[j]])

            try:
                intersection = np.linalg.solve(A, b)
                if all(val >= 0 for val in intersection):  # Ensure non-negative values
                    feasible_region_x.append(intersection[0])
                    feasible_region_y.append(intersection[1])

                    # Compute objective function value
                    z = float(obj_x1 * intersection[0] + obj_x2 * intersection[1])
                    if optimal_value is None or (objective == 'max' and z > optimal_value) or (objective == 'min' and z < optimal_value):
                        optimal_value = z
                        optimal_point = intersection
            except np.linalg.LinAlgError:
                continue  # Skip parallel constraints

    # Check if a feasible region exists
    if len(feasible_region_x) > 0:
        # Fill the feasible region with a shaded color
        plt.fill(feasible_region_x, feasible_region_y, 'lightblue', alpha=0.4, label="Feasible Region")
    else:
        plt.text(5, 5, "No Feasible Region", fontsize=12, color="red")

    # Mark optimal point
    if optimal_point is not None:
        plt.scatter(optimal_point[0], optimal_point[1], color="red", s=100, label="Optimal Solution")
        plt.annotate(f"({optimal_point[0]:.2f}, {optimal_point[1]:.2f})", 
                     (optimal_point[0], optimal_point[1]), 
                     textcoords="offset points", xytext=(5,5), ha='center')

    # Set axis limits dynamically
    plt.xlim(0, max(rhs) + 5)
    plt.ylim(0, max(rhs) + 5)
    plt.xlabel('x₁')
    plt.ylabel('x₂')
    plt.title('Feasible Region for Graphical Method')

    plt.legend()
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return img_str, optimal_point, optimal_value
