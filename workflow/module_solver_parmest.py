import copy

# For solving models
from pyomo.environ import *
from pyomo.dae import *
import matplotlib.pyplot as plt

# For parameter estimation
import pandas as pd
import pyomo.contrib.parmest.parmest as parmest
import importlib.util

class SolverParmestModule():

    def find_optimal_params_and_solve_model(self,input_profile: dict, theta_names: list, model_filepath: str):
        
        """ Solves model iteratively to find optimal parameters.

        Identifies optimal values for model parameters that lead to minimal error between experimental data 
        and model output. Syntax is adapted from parmest documentation and tutorial. If identification of
        ideal parameters fails an exception is thrown.

        Parameters:
            input_profile (dict):
                Contains known properties of system, including parameters, initial guesses for
                variables and the dimensions (and bounds) for modeling.
            theta_names (list):
                List of names of the model parameters that shall be fitted in the solver and 
                parameter estimation module.
            model_filepath (str):
                Filepath of python file with function "create_pyomo_model" that returns pyomo model.
        
        Returns:
            sse (float):
                Returns minimal/optimal summed squared error between experimental data and model
                output achieved by setting the parameters to "theta" (see below).
            theta (list):
                List of optimal parameter values that lead to minimal objective value/SSE.
        """
        
        # Import the file containing the pyomo model
        name = model_filepath
        name = name.replace(".py", "")
        imported_module = importlib.import_module(name)
        
        # Choose error function
        def SSE(model, input_profile):
            expr = sum(
                    #(model.c1_meas[z] - model.c_i[z,1])**2 +
                    #(model.c2_meas[z] - model.c_i[z,2])**2 +
                    ((model.c3_meas[z] - model.c_i[z,3])**2)
                    for z in model.z
            )
            return expr
        
        # Create an instance of parmest estimator
        solver_options = {"max_iter": 12000}    #, "print_level": 5, "tol": 1e-17, "bound_push": 1e-8}  # Options are optional. If provided, include "solver_options" in arguments for "Estimator"
        pest = parmest.Estimator(imported_module.create_pyomo_model, [input_profile], theta_names, SSE, solver_options) # 1st argument: provide method that returns instantiated pyomo model with the params to fit. Values in input_profile are used as starting guesses.

        # Parameter estimation
        obj, theta = pest.theta_est()
        sse = obj

        return sse, theta

    def plot(self,input_profile: dict, theta_names: list, theta: list, model_filepath: str):
        
        """
        Plot the fitted model.

        This method plots (1) the measured experimental truth data, (2) the predicted concentrations
        curves of the model "model_filepath" with initial parameter values, i.e., the parameter
        values specified in the "input_profile", and (3) the predicted concentration curves of the 
        model "model_filepath" with optimized parameter values ("theta_names" and "theta"). No return
        value but creates plot. Makes use of the "solve_model" method below.

        Parameters:
            input_profile (dict):
                Contains known properties of system, including parameters, initial guesses for
                variables and the dimensions (and bounds) for modeling.
            theta_names (list):
                List of names of the model parameters that shall be fitted in the solver and 
                parameter estimation module.
            theta (list):
                List of optimal parameter values that lead to minimal objective value/SSE.
            model_filepath (str):
                Filepath of python file with function "create_pyomo_model" that returns pyomo model.
        
        Returns:
        """

        # CAVE: Currently limited to models with v_A * A + v_B * B => v_C * C
        
        experimental_data = input_profile['c3_meas']
        input_profile_initial = input_profile
        input_profile_estimated = copy.deepcopy(input_profile)
        for p, estimated_parameter in enumerate(theta_names):  # Replace initial values by estimated values.
            input_profile_estimated[estimated_parameter] = theta[p]
        
        # Solve predicted model with initial parameters
        z, c1_init, c2_init, c3_init = self.solve_model(input_profile_initial, model_filepath)
        # Solve predicted model with estimated parameters
        z, c1_est, c2_est, c3_est = self.solve_model(input_profile_estimated, model_filepath)

        plt.plot(z,c1_init,color = 'grey', label = 'w/ initial params')
        plt.plot(z,c2_init,color = 'grey')
        plt.plot(z,c3_init,color = 'grey')

        plt.plot(z,c1_est,color = 'blue', linestyle='dashed', label = 'w/ estimated params')
        plt.plot(z,c2_est,color = 'red', linestyle='dashed')
        plt.plot(z,c3_est,color = 'green', linestyle='dashed')
        
        plt.plot(list(experimental_data.keys()),list(experimental_data.values()),color = 'black', label = 'measurement')

        plt.xlabel('z')
        plt.ylabel('c1 / c2 / c3')
        plt.title('Concentration over length')
        plt.legend(loc='lower right')
        plt.show()


    def solve_model(self, model_data, model_filepath):

        """
        Solve passed pyomo model.

        Solve passed pyomo model given initial guesses for variables. Is used in the method "plot" above.

        Parameters:
            model_data (dict):
                Initial guesses for variables. In our case the input profile.
            model_filepath (str):
                Filepath of python file with function "create_pyomo_model" that returns pyomo model.
        
        Returns:
        """

        # CAVE: Currently limited to models with A + B => C

        # Import the file containing the pyomo model
        name = model_filepath
        name = name.replace(".py","")
        imported_module = importlib.import_module(name)
        
        model = imported_module.create_pyomo_model(model_data)

        # Solve discretized model
        solver = SolverFactory('ipopt')
        results = solver.solve(model)
        results.write()

        # Access results
        z = [z for z in model.z]  # access elements of ContinuousSet object
        c1 = [model.c_i[z,1]() for z in model.z]  # access elements of a Var object
        c2 = [model.c_i[z,2]() for z in model.z]  # access elements of a Var object
        c3 = [model.c_i[z,3]() for z in model.z]  # access elements of a Var object

        return z, c1, c2, c3
