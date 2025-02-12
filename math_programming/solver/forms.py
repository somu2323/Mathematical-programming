from django import forms

class LinearProgrammingForm(forms.Form):
    OBJECTIVE_CHOICES = [
        ('max', 'Maximize'),
        ('min', 'Minimize')
    ]

    METHOD_CHOICES = [
        ('simplex', 'Simplex Method'),
        ('graphical', 'Graphical Method')
    ]
    
    # Dropdown for Method Selection
    method = forms.ChoiceField(choices=METHOD_CHOICES, label="Select Method")

    # Objective Function
    objective = forms.ChoiceField(choices=OBJECTIVE_CHOICES, label="Objective Function")
    
    # Objective Function Coefficients
    obj_x1 = forms.FloatField(label="Coefficient of x1")
    obj_x2 = forms.FloatField(label="Coefficient of x2")
