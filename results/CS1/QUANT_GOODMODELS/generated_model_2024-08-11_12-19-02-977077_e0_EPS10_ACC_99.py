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
   m.compartment3_k0_org = Param(m.p, initialize={1: 0.1})
   m.compartment3_E_org = Param(m.p, initialize={1: 43024.2})
   m.compartment9_k0_org = Param(m.p, initialize={1: 0.1})
   m.interface17_kL_discr = Param(m.i, initialize={1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0})
   m.compartment9_E_aq = Param(m.p, initialize={1: 70111})
   m.interface1_F_conv = Param(m.i, initialize={1: 0, 2: 12.5823, 3: 0, 4: 54.4085, 5: 0, 6: 0})
   m.interface2_V_dot_conv = Param(initialize=1.65)
   m.compartment3_MVp = Param(initialize=584.4)
   m.compartment9_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.compartment9_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.compartment9_E_org = Param(m.p, initialize={1: 43024.2})
   m.compartment9_kL_discr = Param(m.i, initialize={1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0})
   m.compartment3_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.interface17_N = Param(initialize=1000)
   m.compartment9_MV = Param(initialize=189)
   m.compartment6_nu_ip_org = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 0, (3, 1): -1, (4, 1): 0, (5, 1): -1, (6, 1): 1})
   m.compartment6_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.interface17_dp = Param(initialize=1e-05)
   m.interface17_d = Param(initialize=0.17)
   m.compartment6_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.compartment6_E_aq = Param(m.p, initialize={1: 70111})
   m.compartment6_k0_org = Param(m.p, initialize={1: 0.1})
   m.compartment9_ord_ip_org = Param(m.i, m.p, initialize={(1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 0, (5, 1): 1, (6, 1): 0})
   m.compartment3_E_aq = Param(m.p, initialize={1: 70111})
   m.compartment3_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.compartment6_Tref_org = Param(m.p, initialize={1: 317.3})
   m.compartment9_Pp = Param(initialize=1141)
   m.compartment3_nu_ip_org = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 0, (3, 1): -1, (4, 1): 0, (5, 1): -1, (6, 1): 1})
   m.compartment6_E_org = Param(m.p, initialize={1: 43024.2})
   m.compartment3_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.environment_Tc = Param(m.n, initialize={1: 309, 2: 316, 3: 324, 4: 329, 5: 336, 6: 347})
   m.compartment9_Pl = Param(initialize=357.9)
   m.compartment6_kL_discr = Param(m.i, initialize={1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0})
   m.compartment3_ord_ip_org = Param(m.i, m.p, initialize={(1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 0, (5, 1): 1, (6, 1): 0})
   m.compartment9_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.compartment9_Tref_org = Param(m.p, initialize={1: 317.3})
   m.interface2_F_conv = Param(m.i, initialize={1: 0.101805, 2: 0, 3: 0, 4: 0, 5: 13.464, 6: 0})
   m.compartment3_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.compartment6_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.compartment6_MVp = Param(initialize=584.4)
   m.compartment6_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.compartment9_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.compartment9_nu_ip_org = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 0, (3, 1): -1, (4, 1): 0, (5, 1): -1, (6, 1): 1})
   m.compartment3_Tref_org = Param(m.p, initialize={1: 317.3})
   m.interface1_V_dot_conv = Param(initialize=1.2748)
   m.compartment6_ord_ip_org = Param(m.i, m.p, initialize={(1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 0, (5, 1): 1, (6, 1): 0})
   m.interface17_H = Param(m.i, initialize={1: 0.1, 2: 1, 3: 0.1, 4: 0.0034, 5: 0, 6: 0})
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.interface5_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.interface17_KL = Var(m.i, m.n, bounds=(1e-20,10))
   m.compartment6_rho = Var(m.n, bounds=(0.1,1500))
   m.interface14_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.interface5_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.interface17_J_diff = Var(m.i, m.n, bounds=(-1,1))
   m.compartment3_V = Var(bounds=(1e-06,100000.0))
   m.compartment3_vis = Var(m.n, bounds=(1e-20,0.1))
   m.compartment6_k_aq = Var(m.p, m.n, bounds=(0,20))
   m.compartment6_D = Var(m.n, bounds=(1e-20,1))
   m.interface17_A = Var(m.n, bounds=(0,100000000000))
   m.compartment9_r_org = Var(m.p, m.n, bounds=(0,1))
   m.compartment3_phase2R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment9_vis = Var(m.n, bounds=(1e-20,0.1))
   m.compartment6_kL = Var(m.i, m.n, bounds=(1e-20,10))
   m.compartment3_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.interface9_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment6_phase2R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment6_V = Var(bounds=(1e-06,100000.0))
   m.interface13_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment9_D = Var(m.n, bounds=(1e-20,1))
   m.compartment6_lD = Var(m.n, bounds=(-3,3))
   m.interface10_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.interface17_phi = Var(m.n, bounds=(0,1))
   m.compartment9_kL = Var(m.i, m.n, bounds=(1e-20,10))
   m.compartment6_vis = Var(m.n, bounds=(1e-20,0.1))
   m.compartment9_rho = Var(m.n, bounds=(0.1,1500))
   m.compartment9_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.interface10_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment3_lD = Var(m.n, bounds=(-3,3))
   m.compartment9_k_aq = Var(m.p, m.n, bounds=(0,20))
   m.compartment6_k_org = Var(m.p, m.n, bounds=(0,20))
   m.compartment6_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.interface13_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment3_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment6_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment9_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.interface9_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.interface17_a = Var(m.n, bounds=(0,10000000))
   m.compartment3_k_org = Var(m.p, m.n, bounds=(0,20))
   m.compartment6_r_org = Var(m.p, m.n, bounds=(0,1))
   m.interface17_Pv = Var(m.n, bounds=(0.1,10000))
   m.compartment3_k_aq = Var(m.p, m.n, bounds=(0,20))
   m.compartment3_r_org = Var(m.p, m.n, bounds=(0,1))
   m.compartment9_k_org = Var(m.p, m.n, bounds=(0,20))
   m.interface14_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment3_rho = Var(m.n, bounds=(0.1,1500))
   m.compartment9_phase2R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.compartment9_V = Var(bounds=(1e-06,100000.0))
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, i, n):
      return (m.interface5_F_conv[i,n] == (m.interface10_F_conv[i,n] + 0))
   m.eq1 = Constraint(m.i, m.n, rule=_eq1_rule)

   def _eq2_rule(m, i, n):
      return (m.interface5_V_dot_conv[n] == (m.interface10_V_dot_conv[n] + 0))
   m.eq2 = Constraint(m.i, m.n, rule=_eq2_rule)

   def _eq3_rule(m, i, n):
      return (m.interface9_F_conv[i,n] == (m.interface2_F_conv[i] + m.interface1_F_conv[i]))
   m.eq3 = Constraint(m.i, m.n, rule=_eq3_rule)

   def _eq4_rule(m, i, n):
      return (m.interface9_V_dot_conv[n] == (m.interface2_V_dot_conv + m.interface1_V_dot_conv))
   m.eq4 = Constraint(m.i, m.n, rule=_eq4_rule)

   def _eq5_rule(m, i, p, n):
      return (0 == ((m.interface5_F_conv[i,n] - m.interface13_F_conv[i,n]) + ((m.compartment3_V * m.compartment3_phase1R[i,p,n]) + (m.compartment3_V * m.compartment3_phase2R[i,p,n]))))
   m.eq5 = Constraint(m.i, m.p, m.n, rule=_eq5_rule)

   def _eq6_rule(m, n):
      return (m.interface5_V_dot_conv[n] == m.interface13_V_dot_conv[n])
   m.eq6 = Constraint(m.n, rule=_eq6_rule)

   def _eq7_rule(m, i, p, n):
      return (0 == ((m.interface9_F_conv[i,n] - m.interface10_F_conv[i,n]) + ((m.compartment6_V * m.compartment6_phase1R[i,p,n]) + ((m.compartment6_V * m.compartment6_phase2R[i,p,n]) + (m.interface17_A[n] * (0 - m.interface17_J_diff[i,n]))))))
   m.eq7 = Constraint(m.i, m.p, m.n, rule=_eq7_rule)

   def _eq8_rule(m, n):
      return (m.interface9_V_dot_conv[n] == m.interface10_V_dot_conv[n])
   m.eq8 = Constraint(m.n, rule=_eq8_rule)

   def _eq9_rule(m, i, p, n):
      return (0 == ((m.interface13_F_conv[i,n] - m.interface14_F_conv[i,n]) + ((m.compartment9_V * m.compartment9_phase1R[i,p,n]) + ((m.compartment9_V * m.compartment9_phase2R[i,p,n]) + (m.interface17_A[n] * m.interface17_J_diff[i,n])))))
   m.eq9 = Constraint(m.i, m.p, m.n, rule=_eq9_rule)

   def _eq10_rule(m, n):
      return (m.interface13_V_dot_conv[n] == m.interface14_V_dot_conv[n])
   m.eq10 = Constraint(m.n, rule=_eq10_rule)

   def _eq11_rule(m, n):
      return (0.105e5 == (m.compartment3_V + (m.compartment6_V + m.compartment9_V)))
   m.eq11 = Constraint(m.n, rule=_eq11_rule)

   def _eq12_rule(m, i, p, n):
      return (0 == (sum((m.compartment3_r_aq[p,n] * m.compartment3_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment3_phase1R[i,p,n]))
   m.eq12 = Constraint(m.i, m.p, m.n, rule=_eq12_rule)

   def _eq13_rule(m, i, p, n):
      return (0 == (sum((m.compartment9_r_org[p,n] * m.compartment9_nu_ip_org[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment9_phase2R[i,p,n]))
   m.eq13 = Constraint(m.i, m.p, m.n, rule=_eq13_rule)

   def _eq14_rule(m, n):
      return (m.interface17_phi[n] == (m.compartment6_V / (m.compartment6_V + m.compartment9_V)))
   m.eq14 = Constraint(m.n, rule=_eq14_rule)

   def _eq15_rule(m, i, p, n):
      return (0 == (sum((m.compartment6_r_aq[p,n] * m.compartment6_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment6_phase1R[i,p,n]))
   m.eq15 = Constraint(m.i, m.p, m.n, rule=_eq15_rule)

   def _eq16_rule(m, i, p, n):
      return (0 == (sum((m.compartment3_r_org[p,n] * m.compartment3_nu_ip_org[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment3_phase2R[i,p,n]))
   m.eq16 = Constraint(m.i, m.p, m.n, rule=_eq16_rule)

   def _eq17_rule(m, n):
      return (m.interface17_A[n] == (m.interface17_a[n] * (m.compartment6_V + m.compartment9_V)))
   m.eq17 = Constraint(m.n, rule=_eq17_rule)

   def _eq18_rule(m, i, n):
      return (m.interface17_J_diff[i,n] == (m.interface17_KL[i,n] * ((m.interface10_F_conv[i,n] / m.interface9_V_dot_conv[n]) - (m.interface17_H[i] * (m.interface14_F_conv[i,n] / m.interface13_V_dot_conv[n])))))
   m.eq18 = Constraint(m.i, m.n, rule=_eq18_rule)

   def _eq19_rule(m, n):
      return ((1 - m.interface17_phi[n]) == (m.compartment9_V / (m.compartment6_V + m.compartment9_V)))
   m.eq19 = Constraint(m.n, rule=_eq19_rule)

   def _eq20_rule(m, i, p, n):
      return (0 == (sum((m.compartment9_r_aq[p,n] * m.compartment9_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment9_phase1R[i,p,n]))
   m.eq20 = Constraint(m.i, m.p, m.n, rule=_eq20_rule)

   def _eq21_rule(m, i, p, n):
      return (0 == (sum((m.compartment6_r_org[p,n] * m.compartment6_nu_ip_org[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment6_phase2R[i,p,n]))
   m.eq21 = Constraint(m.i, m.p, m.n, rule=_eq21_rule)

   def _eq22_rule(m, p, n):
      return (0 == ((m.compartment6_k_aq[p,n] * prod(((m.interface10_F_conv[i,n] / m.interface9_V_dot_conv[n]) ** m.compartment6_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment6_r_aq[p,n]))
   m.eq22 = Constraint(m.p, m.n, rule=_eq22_rule)

   def _eq23_rule(m, p, n):
      return (0 == ((m.compartment6_k_org[p,n] * prod(((m.interface10_F_conv[i,n] / m.interface9_V_dot_conv[n]) ** m.compartment6_ord_ip_org[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment6_r_org[p,n]))
   m.eq23 = Constraint(m.p, m.n, rule=_eq23_rule)

   def _eq24_rule(m, n):
      return (m.interface17_phi[n] == (m.interface9_V_dot_conv[n] / (m.interface9_V_dot_conv[n] + m.interface13_V_dot_conv[n])))
   m.eq24 = Constraint(m.n, rule=_eq24_rule)

   def _eq25_rule(m, p, n):
      return (0 == ((m.compartment9_k_aq[p,n] * prod(((m.interface14_F_conv[i,n] / m.interface13_V_dot_conv[n]) ** m.compartment9_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment9_r_aq[p,n]))
   m.eq25 = Constraint(m.p, m.n, rule=_eq25_rule)

   def _eq26_rule(m, p, n):
      return (0 == ((m.compartment3_k_org[p,n] * prod(((m.interface13_F_conv[i,n] / m.interface5_V_dot_conv[n]) ** m.compartment3_ord_ip_org[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment3_r_org[p,n]))
   m.eq26 = Constraint(m.p, m.n, rule=_eq26_rule)

   def _eq27_rule(m, n):
      return (m.interface17_a[n] == (6 * (m.interface17_phi[n] / m.interface17_dp)))
   m.eq27 = Constraint(m.n, rule=_eq27_rule)

   def _eq28_rule(m, i, n):
      return (m.interface17_KL[i,n] == (m.interface17_kL_discr[i] * (1 / ((m.interface17_H[i] / (m.compartment9_kL[i,n] + 1e-22)) + (1 / (m.compartment6_kL[i,n] + 1e-22))))))
   m.eq28 = Constraint(m.i, m.n, rule=_eq28_rule)

   def _eq29_rule(m, p, n):
      return (0 == ((m.compartment3_k_aq[p,n] * prod(((m.interface13_F_conv[i,n] / m.interface5_V_dot_conv[n]) ** m.compartment3_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment3_r_aq[p,n]))
   m.eq29 = Constraint(m.p, m.n, rule=_eq29_rule)

   def _eq30_rule(m, p, n):
      return (0 == ((m.compartment9_k_org[p,n] * prod(((m.interface14_F_conv[i,n] / m.interface13_V_dot_conv[n]) ** m.compartment9_ord_ip_org[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment9_r_org[p,n]))
   m.eq30 = Constraint(m.p, m.n, rule=_eq30_rule)

   def _eq31_rule(m, p, n):
      return (m.compartment9_k_aq[p,n] == (m.compartment9_k0_aq[p] * exp((((0 - m.compartment9_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment9_Tref_aq[p]))))))
   m.eq31 = Constraint(m.p, m.n, rule=_eq31_rule)

   def _eq32_rule(m, p, n):
      return (m.compartment3_k_org[p,n] == (m.compartment3_k0_org[p] * exp((((0 - m.compartment3_E_org[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment3_Tref_org[p]))))))
   m.eq32 = Constraint(m.p, m.n, rule=_eq32_rule)

   def _eq33_rule(m, p, n):
      return (m.compartment3_k_aq[p,n] == (m.compartment3_k0_aq[p] * exp((((0 - m.compartment3_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment3_Tref_aq[p]))))))
   m.eq33 = Constraint(m.p, m.n, rule=_eq33_rule)

   def _eq34_rule(m, p, n):
      return (m.compartment6_k_org[p,n] == (m.compartment6_k0_org[p] * exp((((0 - m.compartment6_E_org[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment6_Tref_org[p]))))))
   m.eq34 = Constraint(m.p, m.n, rule=_eq34_rule)

   def _eq35_rule(m, i, n):
      return (m.compartment6_kL[i,n] == (m.compartment6_kL_discr[i] * (0.13 * ((((m.interface17_Pv[n] * m.compartment6_vis[n]) / (m.compartment6_rho[n] * m.compartment6_rho[n])) ** 0.25) * (((m.compartment6_D[n] * m.compartment6_rho[n]) / m.compartment6_vis[n]) ** (2/3))))))
   m.eq35 = Constraint(m.i, m.n, rule=_eq35_rule)

   def _eq36_rule(m, i, n):
      return (m.compartment9_kL[i,n] == (m.compartment9_kL_discr[i] * (0.13 * ((((m.interface17_Pv[n] * m.compartment9_vis[n]) / (m.compartment9_rho[n] * m.compartment9_rho[n])) ** 0.25) * (((m.compartment9_D[n] * m.compartment9_rho[n]) / m.compartment9_vis[n]) ** (2/3))))))
   m.eq36 = Constraint(m.i, m.n, rule=_eq36_rule)

   def _eq37_rule(m, p, n):
      return (m.compartment6_k_aq[p,n] == (m.compartment6_k0_aq[p] * exp((((0 - m.compartment6_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment6_Tref_aq[p]))))))
   m.eq37 = Constraint(m.p, m.n, rule=_eq37_rule)

   def _eq38_rule(m, p, n):
      return (m.compartment9_k_org[p,n] == (m.compartment9_k0_org[p] * exp((((0 - m.compartment9_E_org[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment9_Tref_org[p]))))))
   m.eq38 = Constraint(m.p, m.n, rule=_eq38_rule)

   def _eq39_rule(m, n):
      return (m.interface17_Pv[n] == ((0.2 * ((((1 - m.interface17_phi[n]) * m.compartment6_rho[n]) + (m.interface17_phi[n] * m.compartment9_rho[n])) * (((m.interface17_N / 60) ** 3) * (m.interface17_d ** 5)))) / ((m.compartment6_V + m.compartment9_V) * 1e-5)))
   m.eq39 = Constraint(m.n, rule=_eq39_rule)

   def _eq40_rule(m, n):
      return (m.compartment6_vis[n] == (0.0286 * exp(((-0.012) * m.environment_Tc[n]))))
   m.eq40 = Constraint(m.n, rule=_eq40_rule)

   def _eq41_rule(m, n):
      return (m.compartment9_rho[n] == ((-0.7889 * m.environment_Tc[n]) + 1075.8))
   m.eq41 = Constraint(m.n, rule=_eq41_rule)

   def _eq42_rule(m, n):
      return (m.compartment6_D[n] == (0.0000000125 * (((m.compartment6_MVp ** (-0.19)) - 0.292) * ((m.environment_Tc[n] ** 1.52) * (m.compartment6_vis[n] ** m.compartment6_lD[n])))))
   m.eq42 = Constraint(m.n, rule=_eq42_rule)

   def _eq43_rule(m, n):
      return (m.compartment3_vis[n] == (0.0286 * exp(((-0.012) * m.environment_Tc[n]))))
   m.eq43 = Constraint(m.n, rule=_eq43_rule)

   def _eq44_rule(m, n):
      return (m.compartment3_rho[n] == ((-0.7889 * m.environment_Tc[n]) + 1075.8))
   m.eq44 = Constraint(m.n, rule=_eq44_rule)

   def _eq45_rule(m, n):
      return (m.compartment9_D[n] == (0.0000000155 * ((m.environment_Tc[n] ** 1.29) * ((m.compartment9_Pl ** 0.5) * ((m.compartment9_Pp ** (-0.42)) * ((m.compartment9_vis[n] ** -0.92) * (m.compartment9_MV ** (-0.23))))))))
   m.eq45 = Constraint(m.n, rule=_eq45_rule)

   def _eq46_rule(m, n):
      return (m.compartment3_lD[n] == ((0.958 / m.compartment3_MVp) - 1.12))
   m.eq46 = Constraint(m.n, rule=_eq46_rule)

   def _eq47_rule(m, n):
      return (m.compartment9_vis[n] == (0.0286 * exp(((-0.012) * m.environment_Tc[n]))))
   m.eq47 = Constraint(m.n, rule=_eq47_rule)

   def _eq48_rule(m, n):
      return (m.compartment6_rho[n] == ((-0.0039 * (m.environment_Tc[n] ** 2)) + ((2.0516 * m.environment_Tc[n]) + 727.52)))
   m.eq48 = Constraint(m.n, rule=_eq48_rule)

   def _eq49_rule(m, n):
      return (m.compartment6_lD[n] == ((0.958 / m.compartment6_MVp) - 1.12))
   m.eq49 = Constraint(m.n, rule=_eq49_rule)

   # End: Block 4

   # Set up list of pairs of measured vs. computed variables so that parmest can access them for the objective function
   m.measurement_pairs = []
   for index, var in enumerate(input_profile["measured_var"]):
      m.measurement_pairs.append((m.component(list(var.keys())[0]),input_profile["measured_var_index"][index][list(var.keys())[0]],m.component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas")))
   m.experiments = range(1,input_profile["n_exp"]+1)

   return m