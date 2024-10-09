from pyomo.environ import *
from pyomo.dae import *

def create_pyomo_model(input_profile):
     
   # Choose model class
   m = ConcreteModel()

   # Begin: Block 1
   # Create sets
   # End: Block 1
   # Set up parameters for the measured experimental variables   
   for index, var in enumerate(input_profile["measured_var"]):
      m.add_component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas", Param([1], initialize=input_profile["measured_var"][index][list(var.keys())[0]]))

   # Begin: Block 2
   # Define parameters
   # End: Block 2

   # Begin: Block 3
   # Create variables
   # End: Block 3
   
   # Begin: Block 4
   # Define equations
   # End: Block 4

   discretizer = TransformationFactory('dae.finite_difference')
   discretizer.apply_to(m,nfe=200,wrt=m.V_PFR,scheme='BACKWARD')

   # Set up list of pairs of measured vs. computed variables so that parmest can access them for the objective function
   m.measurement_pairs = []
   for index, var in enumerate(input_profile["measured_var"]):
      m.measurement_pairs.append((m.component(list(var.keys())[0]),input_profile["measured_var_index"][index][list(var.keys())[0]],m.component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas")))
   m.experiments = range(1,input_profile["n_exp"]+1)

   return m