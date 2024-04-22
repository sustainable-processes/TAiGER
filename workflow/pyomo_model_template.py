from pyomo.environ import *
from pyomo.dae import *

def create_pyomo_model(input_profile):
     
   # Choose model class
   m = ConcreteModel()

   # Lines for general set-up. This knowledge is not yet incorporated in the state/equation. CAVE: Find more general implementation if using != 3 components or other resolution/dimensionality than z. 
   m.zOfMeas = Set(initialize=sorted(input_profile["c3_meas"].keys())) # Necessary to ensure that discretization is same in model and experimental data: Used as index for experimental data (next line) and discretization of continuous set.
   m.c3_meas = Param(m.zOfMeas, initialize=input_profile["c3_meas"]) # Necessary to have as model parameter, because used by parmest error function.

   # Begin: Block 1
   # Create sets
   # End: Block 1

   # Lines for general set-up. This knowledge is not yet incorporated in the state/equation. CAVE: Find more general implementation if using != 3 components or other resolution/dimensionality than z. 
   m.c_i0 = Param(m.i, initialize=input_profile["c_i0"])

   # Begin: Block 2
   # Define parameters
   # End: Block 2

   # Begin: Block 3
   # Create variables
   # End: Block 3

   # Begin: Block 4
   # Define equations
   # End: Block 4

   # Discretization Transformations
   discretizer = TransformationFactory('dae.finite_difference')
   discretizer.apply_to(m,nfe=6,wrt=m.z,scheme='BACKWARD') # CENTRAL, FORWARD. 
   #discretizer = TransformationFactory('dae.collocation')
   #discretizer.apply_to(model,nfe=5,ncp=3,scheme='LAGRANGE-RADAU') # LAGRANGE-LEGENDRE.

   return m

