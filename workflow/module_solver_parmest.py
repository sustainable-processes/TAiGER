from pyomo.environ import *
from pyomo.dae import *
import importlib.util

class SolverParmestModule():

    def find_optimal_params_and_solve_model(self,input_profile: dict, theta_names: list, model_filepath: str, solver : str, modus):
                
        # Import the file containing the pyomo model
        name = model_filepath
        name = name.replace(".py", "")
        imported_module = importlib.import_module(name)
        
        base_model = imported_module.create_pyomo_model(input_profile)

        # Choose error function
        if modus == "normal" or modus == "hierarchic_data":
            def SSE(m):
                weight = 1000

                if any(i==999 for (var,i,var_meas) in m.measurement_pairs):
                    var_expr = "var[n]"
                else:
                    var_expr = "var[i,n]"
                expr = sum(
                        (weight*(eval(var_expr) - (var_meas[n])))**2
                        for (var,i,var_meas) in m.measurement_pairs
                        for n in var_meas.index_set()
                        )
                return expr

        elif modus == "rtd":
            def SSE(m):
                if any(i==999 for (var,i,var_meas) in m.measurement_pairs):
                    var_expr = "var[n]"
                else:
                    var_expr = "var[i,n]"
                expr = sum(
                        ((1/(0.0008))*(eval(var_expr) - (var_meas[n])))**2
                        for (var,i,var_meas) in m.measurement_pairs
                        for n in m.tofMeas
                        )
                return expr
        
        # Make it a bit less noisy if no measurement stream can be found
        try:
            base_model.obj = Objective(rule=SSE, sense=minimize)
        except:
            print("No measurement identified.")
        
        # Output
        import sys
        f = open('.\pyomomodel.txt', 'w')
        standard = sys.stdout
        sys.stdout = f
        base_model.pprint()
        sys.stdout = standard
        
        # Use GAMS as the primary interface to access all sorts of solvers
        ## Solver list: https://www.gams.com/latest/docs/S_MAIN.html
        solver = SolverFactory('gams')

        if modus == "normal" or modus == "hierarchic_data":
            try:
                # Set options for used solver
                ## https://www.gams.com/latest/docs/UG_SolverUsage.html#BASIC_USAGE_GAMS_OPTIONS
                io_options = dict(add_options=['GAMS_MODEL.optfile = 1;','$onecho > baron.opt', 'reslim 30\n NumLoc 3\n Threads 8\n', '$offecho'], )
                results = solver.solve(base_model, solver='baron', logfile=".\paramest.log", tee=True, keepfiles=True, io_options=io_options)
            except:
                io_options = dict(add_options=['GAMS_MODEL.optfile = 1;','$onecho > ipopt.opt', 'tol 1e-4\n max_cpu_time 5\n', '$offecho'], )
                results = solver.solve(base_model, solver='ipopt', logfile=".\paramest.log", tee=True, keepfiles=True, io_options=io_options)
        elif modus == "rtd":
            try:
                io_options = dict(add_options=['GAMS_MODEL.optfile = 1;','$onecho > dicopt.opt', 'stop 0\n', '$offecho'], )
                results = solver.solve(base_model, solver='dicopt', logfile=".\paramest.log", tee=True, keepfiles=True, io_options=io_options)
            except:
                io_options = dict(add_options=['GAMS_MODEL.optfile = 1;','$onecho > ipopt.opt', 'tol 1e-4\n max_cpu_time 5\n', '$offecho'], )
                results = solver.solve(base_model, solver='ipopt', logfile=".\paramest.log", tee=True, keepfiles=True, io_options=io_options)

        
        # If solver exceeds maximum time, use best upper bound for objective
        if results.solver.termination_condition == TerminationCondition.maxTimeLimit:
             obj = results["Solver"][0]["Primal bound"]
        else:
            obj = value(base_model.obj)

        return obj, base_model