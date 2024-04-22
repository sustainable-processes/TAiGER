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
   m.p = RangeSet(1,1)
   m.z = ContinuousSet(bounds=(0,0.1), initialize=m.zOfMeas)
   m.i = RangeSet(1,3)
   # End: Block 1

   # Lines for general set-up. This knowledge is not yet incorporated in the state/equation. CAVE: Find more general implementation if using != 3 components or other resolution/dimensionality than z. 
   m.c_i0 = Param(m.i, initialize=input_profile["c_i0"])

   # Begin: Block 2
   # Define parameters
   m.d_v_z_dz = Param(m.z, m.i, initialize=0)
   m.D_z = Param(initialize=input_profile["D_z"], mutable=True) # This parameter is to be estimated.
   m.k_p = Param(m.p, initialize=input_profile["k_p"], mutable=True) # This parameter is to be estimated.
   m.v_z = Param(initialize=0.001)
   m.nu_ip = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -2, (3, 1): 1})
   m.ord_ip = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 2, (3, 1): 0})
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.j_i = Var(m.z, m.i)
   m.r_i = Var(m.z, m.i)
   m.c_i = Var(m.z, m.i)
   m.r_p = Var(m.z, m.p)
   m.d_j_i_dz = DerivativeVar(m.j_i, wrt=m.z)
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

   def _eq3_rule(m, z, i):
      return (0 == ((-1 * (m.D_z * m.d_c_i_dz[z,i])) - m.j_i[z,i]))
   m.eq3 = Constraint(m.z, m.i, rule=_eq3_rule)

   def _eq4_rule(m, i):
      return (0 == m.d_j_i_dz[input_profile['sets']['z']['max'],i])
   m.eq4 = Constraint(m.i, rule=_eq4_rule)

   def _eq5_rule(m, z, i):
      return (0 == (sum((m.r_p[z, p] * m.nu_ip[i, p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.r_i[z,i]))
   m.eq5 = Constraint(m.z, m.i, rule=_eq5_rule)

   def _eq6_rule(m, z, p):
      return (0 == ((m.k_p[p] * prod((m.c_i[z,i] ** m.ord_ip[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.r_p[z, p]))
   m.eq6 = Constraint(m.z, m.p, rule=_eq6_rule)

   # End: Block 4

   # Discretization Transformations
   discretizer = TransformationFactory('dae.finite_difference')
   discretizer.apply_to(m,nfe=6,wrt=m.z,scheme='BACKWARD') # CENTRAL, FORWARD. 
   #discretizer = TransformationFactory('dae.collocation')
   #discretizer.apply_to(model,nfe=5,ncp=3,scheme='LAGRANGE-RADAU') # LAGRANGE-LEGENDRE.

   return m

