from pyomo.environ import *
from pyomo.dae import *

def create_pyomo_model(input_profile):
     
   # Choose model class
   m = ConcreteModel()

   # Begin: Block 1
   # Create sets
   m.p = RangeSet(1,1)
   m.i = RangeSet(1,6)
   m.n = RangeSet(1,6)
   # End: Block 1
   # Set up parameters for the measured experimental variables
   for index, var in enumerate(input_profile["measured_var"]):
      m.add_component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas", Param(m.n, initialize=input_profile["measured_var"][index][list(var.keys())[0]]))
   
   # Begin: Block 2
   # Define parameters
   m.interface3_F_conv = Param(m.i, initialize={1: 0.101805, 2: 0, 3: 0, 4: 0, 5: 13.464, 6: 0})
   m.interface3_V_dot_conv = Param(initialize=1.65)
   m.compartment1_nu_ip_org = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 0, (3, 1): -1, (4, 1): 0, (5, 1): -1, (6, 1): 1})
   m.compartment1_E_org = Param(m.p, initialize={1: 43024.2})
   m.compartment1_ord_ip_org = Param(m.i, m.p, initialize={(1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 0, (5, 1): 1, (6, 1): 0})
   m.compartment1_Tref_org = Param(m.p, initialize={1: 317.3})
   m.environment_Tc = Param(m.n, initialize={1: 309, 2: 316, 3: 324, 4: 329, 5: 336, 6: 347})
   m.compartment1_k0_org = Param(m.p, initialize={1: 0.1})
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.compartment1_V = Var(bounds=(1e-06,100000.0))
   m.compartment1_r_org = Var(m.p, m.n, bounds=(0,1))
   m.compartment1_k_org = Var(m.p, m.n, bounds=(0,20))
   m.compartment1_phase2R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.interface4_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.interface4_F_conv = Var(m.i, m.n, bounds=(0,100))
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, i, p, n):
      return (0 == ((m.interface3_F_conv[i] - m.interface4_F_conv[i,n]) + (m.compartment1_V * m.compartment1_phase2R[i,p,n])))
   m.eq1 = Constraint(m.i, m.p, m.n, rule=_eq1_rule)

   def _eq2_rule(m, n):
      return (m.interface3_V_dot_conv == m.interface4_V_dot_conv[n])
   m.eq2 = Constraint(m.n, rule=_eq2_rule)

   def _eq3_rule(m, n):
      return (0.105e5 == m.compartment1_V)
   m.eq3 = Constraint(m.n, rule=_eq3_rule)

   def _eq4_rule(m, i, p, n):
      return (0 == (sum((m.compartment1_r_org[p,n] * m.compartment1_nu_ip_org[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment1_phase2R[i,p,n]))
   m.eq4 = Constraint(m.i, m.p, m.n, rule=_eq4_rule)

   def _eq5_rule(m, p, n):
      return (0 == ((m.compartment1_k_org[p,n] * prod(((m.interface4_F_conv[i,n] / m.interface3_V_dot_conv) ** m.compartment1_ord_ip_org[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment1_r_org[p,n]))
   m.eq5 = Constraint(m.p, m.n, rule=_eq5_rule)

   def _eq6_rule(m, p, n):
      return (m.compartment1_k_org[p,n] == (m.compartment1_k0_org[p] * exp((((0 - m.compartment1_E_org[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment1_Tref_org[p]))))))
   m.eq6 = Constraint(m.p, m.n, rule=_eq6_rule)

   # End: Block 4

   # Set up list of pairs of measured vs. computed variables so that parmest can access them for the objective function
   m.measurement_pairs = []
   for index, var in enumerate(input_profile["measured_var"]):
      m.measurement_pairs.append((m.component(list(var.keys())[0]),input_profile["measured_var_index"][index][list(var.keys())[0]],m.component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas")))
   m.experiments = range(1,input_profile["n_exp"]+1)

   return m