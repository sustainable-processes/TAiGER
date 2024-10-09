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
   m.compartment4_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.interface3_V_dot_conv = Param(initialize=1.2748)
   m.compartment4_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.compartment4_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.compartment1_E_aq = Param(m.p, initialize={1: 70111})
   m.interface2_F_conv = Param(m.i, initialize={1: 0.101805, 2: 0, 3: 0, 4: 0, 5: 13.464, 6: 0})
   m.interface3_F_conv = Param(m.i, initialize={1: 0, 2: 12.5823, 3: 0, 4: 54.4085, 5: 0, 6: 0})
   m.compartment1_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.compartment1_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.compartment1_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.compartment4_E_aq = Param(m.p, initialize={1: 70111})
   m.compartment1_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.environment_Tc = Param(m.n, initialize={1: 309, 2: 316, 3: 324, 4: 329, 5: 336, 6: 347})
   m.compartment4_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.interface2_V_dot_conv = Param(initialize=1.65)
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.compartment1_V = Var(bounds=(1e-06,100000.0))
   m.interface11_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.interface8_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.interface11_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.interface7_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.interface8_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment1_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment4_k_aq = Var(m.p, m.n, bounds=(0,20))
   m.compartment4_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.interface7_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment4_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.compartment1_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.compartment4_V = Var(bounds=(1e-06,100000.0))
   m.compartment1_k_aq = Var(m.p, m.n, bounds=(0,20))
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, i, p, n):
      return (0 == ((m.interface3_F_conv[i] - m.interface7_F_conv[i,n]) + (m.compartment1_V * m.compartment1_phase1R[i,p,n])))
   m.eq1 = Constraint(m.i, m.p, m.n, rule=_eq1_rule)

   def _eq2_rule(m, n):
      return (m.interface3_V_dot_conv == m.interface7_V_dot_conv[n])
   m.eq2 = Constraint(m.n, rule=_eq2_rule)

   def _eq3_rule(m, i, p, n):
      return (0 == ((m.interface7_F_conv[i,n] - m.interface8_F_conv[i,n]) + (m.compartment4_V * m.compartment4_phase1R[i,p,n])))
   m.eq3 = Constraint(m.i, m.p, m.n, rule=_eq3_rule)

   def _eq4_rule(m, n):
      return (m.interface7_V_dot_conv[n] == m.interface8_V_dot_conv[n])
   m.eq4 = Constraint(m.n, rule=_eq4_rule)

   def _eq5_rule(m, i, n):
      return (m.interface11_F_conv[i,n] == (m.interface2_F_conv[i] + m.interface8_F_conv[i,n]))
   m.eq5 = Constraint(m.i, m.n, rule=_eq5_rule)

   def _eq6_rule(m, i, n):
      return (m.interface11_V_dot_conv[n] == (m.interface2_V_dot_conv + m.interface8_V_dot_conv[n]))
   m.eq6 = Constraint(m.i, m.n, rule=_eq6_rule)

   def _eq7_rule(m, n):
      return (0.105e5 == (m.compartment1_V + m.compartment4_V))
   m.eq7 = Constraint(m.n, rule=_eq7_rule)

   def _eq8_rule(m, n):
      return ((0.43585886214442016 * 0.105e5) == (m.compartment1_V + m.compartment4_V))
   m.eq8 = Constraint(m.n, rule=_eq8_rule)

   def _eq9_rule(m, i, p, n):
      return (0 == (sum((m.compartment4_r_aq[p,n] * m.compartment4_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment4_phase1R[i,p,n]))
   m.eq9 = Constraint(m.i, m.p, m.n, rule=_eq9_rule)

   def _eq10_rule(m, i, p, n):
      return (0 == (sum((m.compartment1_r_aq[p,n] * m.compartment1_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment1_phase1R[i,p,n]))
   m.eq10 = Constraint(m.i, m.p, m.n, rule=_eq10_rule)

   def _eq11_rule(m, p, n):
      return (0 == ((m.compartment1_k_aq[p,n] * prod(((m.interface7_F_conv[i,n] / m.interface3_V_dot_conv) ** m.compartment1_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment1_r_aq[p,n]))
   m.eq11 = Constraint(m.p, m.n, rule=_eq11_rule)

   def _eq12_rule(m, p, n):
      return (0 == ((m.compartment4_k_aq[p,n] * prod(((m.interface8_F_conv[i,n] / m.interface7_V_dot_conv[n]) ** m.compartment4_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment4_r_aq[p,n]))
   m.eq12 = Constraint(m.p, m.n, rule=_eq12_rule)

   def _eq13_rule(m, p, n):
      return (m.compartment1_k_aq[p,n] == (m.compartment1_k0_aq[p] * exp((((0 - m.compartment1_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment1_Tref_aq[p]))))))
   m.eq13 = Constraint(m.p, m.n, rule=_eq13_rule)

   def _eq14_rule(m, p, n):
      return (m.compartment4_k_aq[p,n] == (m.compartment4_k0_aq[p] * exp((((0 - m.compartment4_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment4_Tref_aq[p]))))))
   m.eq14 = Constraint(m.p, m.n, rule=_eq14_rule)

   # End: Block 4

   # Set up list of pairs of measured vs. computed variables so that parmest can access them for the objective function
   m.measurement_pairs = []
   for index, var in enumerate(input_profile["measured_var"]):
      m.measurement_pairs.append((m.component(list(var.keys())[0]),input_profile["measured_var_index"][index][list(var.keys())[0]],m.component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas")))
   m.experiments = range(1,input_profile["n_exp"]+1)

   return m