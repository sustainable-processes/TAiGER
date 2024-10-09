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
   m.compartment8_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.compartment5_E_aq = Param(m.p, initialize={1: 70111})
   m.interface4_F_conv = Param(m.i, initialize={1: 0.101805, 2: 0, 3: 0, 4: 0, 5: 13.464, 6: 0})
   m.compartment2_E_org = Param(m.p, initialize={1: 43024.2})
   m.compartment5_nu_ip_org = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 0, (3, 1): -1, (4, 1): 0, (5, 1): -1, (6, 1): 1})
   m.compartment8_E_aq = Param(m.p, initialize={1: 70111})
   m.compartment5_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.compartment5_k0_org = Param(m.p, initialize={1: 0.1})
   m.compartment5_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.compartment8_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.compartment5_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.compartment2_ord_ip_org = Param(m.i, m.p, initialize={(1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 0, (5, 1): 1, (6, 1): 0})
   m.compartment5_ord_ip_org = Param(m.i, m.p, initialize={(1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 0, (5, 1): 1, (6, 1): 0})
   m.interface4_V_dot_conv = Param(initialize=1.65)
   m.compartment2_Tref_org = Param(m.p, initialize={1: 317.3})
   m.compartment8_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.interface12_F_conv = Param(m.i, initialize={1: 0, 2: 12.5823, 3: 0, 4: 54.4085, 5: 0, 6: 0})
   m.compartment5_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.environment_Tc = Param(m.n, initialize={1: 309, 2: 316, 3: 324, 4: 329, 5: 336, 6: 347})
   m.compartment5_Tref_org = Param(m.p, initialize={1: 317.3})
   m.compartment2_k0_org = Param(m.p, initialize={1: 0.1})
   m.interface12_V_dot_conv = Param(initialize=1.2748)
   m.compartment2_nu_ip_org = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 0, (3, 1): -1, (4, 1): 0, (5, 1): -1, (6, 1): 1})
   m.compartment8_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.compartment5_E_org = Param(m.p, initialize={1: 43024.2})
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.interface5_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment2_phase2R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment8_V = Var(bounds=(1e-06,100000.0))
   m.compartment5_phase2R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment2_V = Var(bounds=(1e-06,100000.0))
   m.interface5_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment2_r_org = Var(m.p, m.n, bounds=(0,1))
   m.compartment8_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.interface9_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment5_V = Var(bounds=(1e-06,100000.0))
   m.interface8_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.interface13_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment8_k_aq = Var(m.p, m.n, bounds=(0,20))
   m.compartment5_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.compartment5_k_org = Var(m.p, m.n, bounds=(0,20))
   m.compartment5_k_aq = Var(m.p, m.n, bounds=(0,20))
   m.interface8_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.interface13_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment8_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.interface9_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment5_r_org = Var(m.p, m.n, bounds=(0,1))
   m.compartment5_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment2_k_org = Var(m.p, m.n, bounds=(0,20))
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, i, n):
      return (m.interface8_F_conv[i,n] == (m.interface5_F_conv[i,n] + m.interface13_F_conv[i,n]))
   m.eq1 = Constraint(m.i, m.n, rule=_eq1_rule)

   def _eq2_rule(m, i, n):
      return (m.interface8_V_dot_conv[n] == (m.interface5_V_dot_conv[n] + m.interface13_V_dot_conv[n]))
   m.eq2 = Constraint(m.i, m.n, rule=_eq2_rule)

   def _eq3_rule(m, i, p, n):
      return (0 == ((m.interface4_F_conv[i] - m.interface5_F_conv[i,n]) + (m.compartment2_V * m.compartment2_phase2R[i,p,n])))
   m.eq3 = Constraint(m.i, m.p, m.n, rule=_eq3_rule)

   def _eq4_rule(m, n):
      return (m.interface4_V_dot_conv == m.interface5_V_dot_conv[n])
   m.eq4 = Constraint(m.n, rule=_eq4_rule)

   def _eq5_rule(m, i, p, n):
      return (0 == ((m.interface8_F_conv[i,n] - m.interface9_F_conv[i,n]) + ((m.compartment5_V * m.compartment5_phase2R[i,p,n]) + (m.compartment5_V * m.compartment5_phase1R[i,p,n]))))
   m.eq5 = Constraint(m.i, m.p, m.n, rule=_eq5_rule)

   def _eq6_rule(m, n):
      return (m.interface8_V_dot_conv[n] == m.interface9_V_dot_conv[n])
   m.eq6 = Constraint(m.n, rule=_eq6_rule)

   def _eq7_rule(m, i, p, n):
      return (0 == ((m.interface12_F_conv[i] - m.interface13_F_conv[i,n]) + (m.compartment8_V * m.compartment8_phase1R[i,p,n])))
   m.eq7 = Constraint(m.i, m.p, m.n, rule=_eq7_rule)

   def _eq8_rule(m, n):
      return (m.interface12_V_dot_conv == m.interface13_V_dot_conv[n])
   m.eq8 = Constraint(m.n, rule=_eq8_rule)

   def _eq9_rule(m, n):
      return (0.105e5 == (m.compartment2_V + (m.compartment5_V + m.compartment8_V)))
   m.eq9 = Constraint(m.n, rule=_eq9_rule)

   def _eq10_rule(m, n):
      return ((0.43585886214442016 * 0.105e5) == m.compartment8_V)
   m.eq10 = Constraint(m.n, rule=_eq10_rule)

   def _eq11_rule(m, i, p, n):
      return (0 == (sum((m.compartment5_r_org[p,n] * m.compartment5_nu_ip_org[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment5_phase2R[i,p,n]))
   m.eq11 = Constraint(m.i, m.p, m.n, rule=_eq11_rule)

   def _eq12_rule(m, i, p, n):
      return (0 == (sum((m.compartment2_r_org[p,n] * m.compartment2_nu_ip_org[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment2_phase2R[i,p,n]))
   m.eq12 = Constraint(m.i, m.p, m.n, rule=_eq12_rule)

   def _eq13_rule(m, i, p, n):
      return (0 == (sum((m.compartment5_r_aq[p,n] * m.compartment5_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment5_phase1R[i,p,n]))
   m.eq13 = Constraint(m.i, m.p, m.n, rule=_eq13_rule)

   def _eq14_rule(m, i, p, n):
      return (0 == (sum((m.compartment8_r_aq[p,n] * m.compartment8_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment8_phase1R[i,p,n]))
   m.eq14 = Constraint(m.i, m.p, m.n, rule=_eq14_rule)

   def _eq15_rule(m, p, n):
      return (0 == ((m.compartment2_k_org[p,n] * prod(((m.interface5_F_conv[i,n] / m.interface4_V_dot_conv) ** m.compartment2_ord_ip_org[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment2_r_org[p,n]))
   m.eq15 = Constraint(m.p, m.n, rule=_eq15_rule)

   def _eq16_rule(m, p, n):
      return (0 == ((m.compartment5_k_org[p,n] * prod(((m.interface9_F_conv[i,n] / m.interface8_V_dot_conv[n]) ** m.compartment5_ord_ip_org[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment5_r_org[p,n]))
   m.eq16 = Constraint(m.p, m.n, rule=_eq16_rule)

   def _eq17_rule(m, p, n):
      return (0 == ((m.compartment5_k_aq[p,n] * prod(((m.interface9_F_conv[i,n] / m.interface8_V_dot_conv[n]) ** m.compartment5_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment5_r_aq[p,n]))
   m.eq17 = Constraint(m.p, m.n, rule=_eq17_rule)

   def _eq18_rule(m, p, n):
      return (0 == ((m.compartment8_k_aq[p,n] * prod(((m.interface13_F_conv[i,n] / m.interface12_V_dot_conv) ** m.compartment8_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment8_r_aq[p,n]))
   m.eq18 = Constraint(m.p, m.n, rule=_eq18_rule)

   def _eq19_rule(m, p, n):
      return (m.compartment5_k_org[p,n] == (m.compartment5_k0_org[p] * exp((((0 - m.compartment5_E_org[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment5_Tref_org[p]))))))
   m.eq19 = Constraint(m.p, m.n, rule=_eq19_rule)

   def _eq20_rule(m, p, n):
      return (m.compartment2_k_org[p,n] == (m.compartment2_k0_org[p] * exp((((0 - m.compartment2_E_org[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment2_Tref_org[p]))))))
   m.eq20 = Constraint(m.p, m.n, rule=_eq20_rule)

   def _eq21_rule(m, p, n):
      return (m.compartment8_k_aq[p,n] == (m.compartment8_k0_aq[p] * exp((((0 - m.compartment8_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment8_Tref_aq[p]))))))
   m.eq21 = Constraint(m.p, m.n, rule=_eq21_rule)

   def _eq22_rule(m, p, n):
      return (m.compartment5_k_aq[p,n] == (m.compartment5_k0_aq[p] * exp((((0 - m.compartment5_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment5_Tref_aq[p]))))))
   m.eq22 = Constraint(m.p, m.n, rule=_eq22_rule)

   # End: Block 4

   # Set up list of pairs of measured vs. computed variables so that parmest can access them for the objective function
   m.measurement_pairs = []
   for index, var in enumerate(input_profile["measured_var"]):
      m.measurement_pairs.append((m.component(list(var.keys())[0]),input_profile["measured_var_index"][index][list(var.keys())[0]],m.component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas")))
   m.experiments = range(1,input_profile["n_exp"]+1)

   return m