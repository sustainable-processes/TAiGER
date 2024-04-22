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
   m.z = ContinuousSet(bounds=(0,0.1), initialize=m.zOfMeas)
   m.i = RangeSet(1,3)
   # End: Block 1

   # Lines for general set-up. This knowledge is not yet incorporated in the state/equation. CAVE: Find more general implementation if using != 3 components or other resolution/dimensionality than z. 
   m.c_i0 = Param(m.i, initialize=input_profile["c_i0"])

   # Begin: Block 2
   # Define parameters
   m.d_j_i_dz = Param(m.z, m.i, initialize=input_profile["d_j_i_dz"], mutable=True) # This parameter is to be estimated.
   m.r_i = Param(m.z, m.i, initialize=0)
   m.d_v_z_dz = Param(m.z, m.i, initialize=0)
   m.v_z = Param(initialize=0.001)
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.c_i = Var(m.z, m.i)
   m.d_c_i_dz = DerivativeVar(m.c_i, wrt=m.z)
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, z, i):
      return (0 == ((m.v_z * m.d_c_i_dz[z,i]) + ((m.c_i[z,i] * m.d_v_z_dz[z,i]) + (m.d_j_i_dz[z,i] - m.r_i[z,i]))))
   m.eq1 = Constraint(m.z, m.i, rule=_eq1_rule)

   def _eq2_rule(m, i):
      return (0 == m.c_i[0,i] - m.c_i0[i])
   m.eq2 = Constraint(m.i, rule=_eq2_rule)

   # End: Block 4

   # Discretization Transformations
   discretizer = TransformationFactory('dae.finite_difference')
   discretizer.apply_to(m,nfe=6,wrt=m.z,scheme='BACKWARD') # CENTRAL, FORWARD. 
   #discretizer = TransformationFactory('dae.collocation')
   #discretizer.apply_to(model,nfe=5,ncp=3,scheme='LAGRANGE-RADAU') # LAGRANGE-LEGENDRE.

   return m

