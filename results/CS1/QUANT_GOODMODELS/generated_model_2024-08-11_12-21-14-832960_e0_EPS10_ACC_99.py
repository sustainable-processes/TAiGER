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
   m.interface12_kL_discr = Param(m.i, initialize={1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0})
   m.compartment5_E_aq = Param(m.p, initialize={1: 70111})
   m.compartment1_Pp = Param(initialize=1141)
   m.compartment5_MVp = Param(initialize=584.4)
   m.compartment1_MV = Param(initialize=189)
   m.compartment5_nu_ip_aq = Param(m.i, m.p, initialize={(1, 1): -1, (2, 1): -1, (3, 1): 1, (4, 1): 1, (5, 1): 0, (6, 1): 0})
   m.compartment1_kL_discr = Param(m.i, initialize={1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0})
   m.compartment5_Tref_aq = Param(m.p, initialize={1: 317.3})
   m.interface12_H = Param(m.i, initialize={1: 0.1, 2: 1, 3: 0.1, 4: 0.0034, 5: 0, 6: 0})
   m.interface12_dp = Param(initialize=1e-05)
   m.interface12_d = Param(initialize=0.17)
   m.compartment5_k0_aq = Param(m.p, initialize={1: 0.0126092})
   m.compartment1_nu_ip_org = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 0, (3, 1): -1, (4, 1): 0, (5, 1): -1, (6, 1): 1})
   m.compartment1_E_org = Param(m.p, initialize={1: 43024.2})
   m.interface12_N = Param(initialize=1000)
   m.compartment5_ord_ip_aq = Param(m.i, m.p, initialize={(1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0})
   m.environment_Tc = Param(m.n, initialize={1: 309, 2: 316, 3: 324, 4: 329, 5: 336, 6: 347})
   m.interface3_F_conv = Param(m.i, initialize={1: 0.101805, 2: 0, 3: 0, 4: 0, 5: 13.464, 6: 0})
   m.interface3_V_dot_conv = Param(initialize=1.65)
   m.compartment1_ord_ip_org = Param(m.i, m.p, initialize={(1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 0, (5, 1): 1, (6, 1): 0})
   m.compartment1_Tref_org = Param(m.p, initialize={1: 317.3})
   m.interface8_F_conv = Param(m.i, initialize={1: 0, 2: 12.5823, 3: 0, 4: 54.4085, 5: 0, 6: 0})
   m.compartment1_Pl = Param(initialize=357.9)
   m.interface8_V_dot_conv = Param(initialize=1.2748)
   m.compartment5_kL_discr = Param(m.i, initialize={1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0})
   m.compartment1_k0_org = Param(m.p, initialize={1: 0.1})
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.interface7_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.interface12_KL = Var(m.i, m.n, bounds=(1e-20,10))
   m.compartment1_D = Var(m.n, bounds=(1e-20,1))
   m.interface4_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment1_kL = Var(m.i, m.n, bounds=(1e-20,10))
   m.compartment1_V = Var(bounds=(1e-06,100000.0))
   m.interface9_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.compartment5_V = Var(bounds=(1e-06,100000.0))
   m.interface4_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment5_vis = Var(m.n, bounds=(1e-20,0.1))
   m.compartment5_r_aq = Var(m.p, m.n, bounds=(0,1))
   m.compartment1_r_org = Var(m.p, m.n, bounds=(0,1))
   m.compartment5_k_aq = Var(m.p, m.n, bounds=(0,20))
   m.compartment1_k_org = Var(m.p, m.n, bounds=(0,20))
   m.compartment1_phase2R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.interface12_Pv = Var(m.n, bounds=(0.1,10000))
   m.interface7_F_conv = Var(m.i, m.n, bounds=(0,100))
   m.interface9_V_dot_conv = Var(m.n, bounds=(1e-06,100))
   m.compartment5_rho = Var(m.n, bounds=(0.1,1500))
   m.compartment5_phase1R = Var(m.i, m.p, m.n, bounds=(-1,1))
   m.interface12_a = Var(m.n, bounds=(0,10000000))
   m.compartment1_vis = Var(m.n, bounds=(1e-20,0.1))
   m.compartment1_rho = Var(m.n, bounds=(0.1,1500))
   m.compartment5_kL = Var(m.i, m.n, bounds=(1e-20,10))
   m.interface12_A = Var(m.n, bounds=(0,100000000000))
   m.compartment5_D = Var(m.n, bounds=(1e-20,1))
   m.interface12_J_diff = Var(m.i, m.n, bounds=(-1,1))
   m.interface12_phi = Var(m.n, bounds=(0,1))
   m.compartment5_lD = Var(m.n, bounds=(-3,3))
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, i, p, n):
      return (0 == ((m.interface3_F_conv[i] - m.interface4_F_conv[i,n]) + ((m.compartment1_V * m.compartment1_phase2R[i,p,n]) + (m.interface12_A[n] * m.interface12_J_diff[i,n]))))
   m.eq1 = Constraint(m.i, m.p, m.n, rule=_eq1_rule)

   def _eq2_rule(m, n):
      return (m.interface3_V_dot_conv == m.interface4_V_dot_conv[n])
   m.eq2 = Constraint(m.n, rule=_eq2_rule)

   def _eq3_rule(m, i, n):
      return (m.interface7_F_conv[i,n] == (m.interface4_F_conv[i,n] + m.interface9_F_conv[i,n]))
   m.eq3 = Constraint(m.i, m.n, rule=_eq3_rule)

   def _eq4_rule(m, i, n):
      return (m.interface7_V_dot_conv[n] == (m.interface4_V_dot_conv[n] + m.interface9_V_dot_conv[n]))
   m.eq4 = Constraint(m.i, m.n, rule=_eq4_rule)

   def _eq5_rule(m, i, p, n):
      return (0 == ((m.interface8_F_conv[i] - m.interface9_F_conv[i,n]) + ((m.compartment5_V * m.compartment5_phase1R[i,p,n]) + (m.interface12_A[n] * (0 - m.interface12_J_diff[i,n])))))
   m.eq5 = Constraint(m.i, m.p, m.n, rule=_eq5_rule)

   def _eq6_rule(m, n):
      return (m.interface8_V_dot_conv == m.interface9_V_dot_conv[n])
   m.eq6 = Constraint(m.n, rule=_eq6_rule)

   def _eq7_rule(m, n):
      return (0.105e5 == (m.compartment1_V + m.compartment5_V))
   m.eq7 = Constraint(m.n, rule=_eq7_rule)

   def _eq8_rule(m, n):
      return ((0.43585886214442016 * 0.105e5) == m.compartment5_V)
   m.eq8 = Constraint(m.n, rule=_eq8_rule)

   def _eq9_rule(m, n):
      return (m.interface12_phi[n] == (m.compartment5_V / (m.compartment5_V + m.compartment1_V)))
   m.eq9 = Constraint(m.n, rule=_eq9_rule)

   def _eq10_rule(m, i, p, n):
      return (0 == (sum((m.compartment1_r_org[p,n] * m.compartment1_nu_ip_org[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment1_phase2R[i,p,n]))
   m.eq10 = Constraint(m.i, m.p, m.n, rule=_eq10_rule)

   def _eq11_rule(m, n):
      return (m.interface12_A[n] == (m.interface12_a[n] * (m.compartment5_V + m.compartment1_V)))
   m.eq11 = Constraint(m.n, rule=_eq11_rule)

   def _eq12_rule(m, i, n):
      return (m.interface12_J_diff[i,n] == (m.interface12_KL[i,n] * ((m.interface9_F_conv[i,n] / m.interface8_V_dot_conv) - (m.interface12_H[i] * (m.interface4_F_conv[i,n] / m.interface3_V_dot_conv)))))
   m.eq12 = Constraint(m.i, m.n, rule=_eq12_rule)

   def _eq13_rule(m, n):
      return ((1 - m.interface12_phi[n]) == (m.compartment1_V / (m.compartment5_V + m.compartment1_V)))
   m.eq13 = Constraint(m.n, rule=_eq13_rule)

   def _eq14_rule(m, i, p, n):
      return (0 == (sum((m.compartment5_r_aq[p,n] * m.compartment5_nu_ip_aq[i,p]) for p in range(1,1+input_profile['sets']['p']['max'])) - m.compartment5_phase1R[i,p,n]))
   m.eq14 = Constraint(m.i, m.p, m.n, rule=_eq14_rule)

   def _eq15_rule(m, n):
      return (m.interface12_phi[n] == (m.interface8_V_dot_conv / (m.interface8_V_dot_conv + m.interface3_V_dot_conv)))
   m.eq15 = Constraint(m.n, rule=_eq15_rule)

   def _eq16_rule(m, p, n):
      return (0 == ((m.compartment1_k_org[p,n] * prod(((m.interface4_F_conv[i,n] / m.interface3_V_dot_conv) ** m.compartment1_ord_ip_org[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment1_r_org[p,n]))
   m.eq16 = Constraint(m.p, m.n, rule=_eq16_rule)

   def _eq17_rule(m, n):
      return (m.interface12_a[n] == (6 * (m.interface12_phi[n] / m.interface12_dp)))
   m.eq17 = Constraint(m.n, rule=_eq17_rule)

   def _eq18_rule(m, i, n):
      return (m.interface12_KL[i,n] == (m.interface12_kL_discr[i] * (1 / ((m.interface12_H[i] / (m.compartment1_kL[i,n] + 1e-22)) + (1 / (m.compartment5_kL[i,n] + 1e-22))))))
   m.eq18 = Constraint(m.i, m.n, rule=_eq18_rule)

   def _eq19_rule(m, p, n):
      return (0 == ((m.compartment5_k_aq[p,n] * prod(((m.interface9_F_conv[i,n] / m.interface8_V_dot_conv) ** m.compartment5_ord_ip_aq[i,p]) for i in range(1,1+input_profile['sets']['i']['max']))) - m.compartment5_r_aq[p,n]))
   m.eq19 = Constraint(m.p, m.n, rule=_eq19_rule)

   def _eq20_rule(m, p, n):
      return (m.compartment1_k_org[p,n] == (m.compartment1_k0_org[p] * exp((((0 - m.compartment1_E_org[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment1_Tref_org[p]))))))
   m.eq20 = Constraint(m.p, m.n, rule=_eq20_rule)

   def _eq21_rule(m, i, n):
      return (m.compartment1_kL[i,n] == (m.compartment1_kL_discr[i] * (0.13 * ((((m.interface12_Pv[n] * m.compartment1_vis[n]) / (m.compartment1_rho[n] * m.compartment1_rho[n])) ** 0.25) * (((m.compartment1_D[n] * m.compartment1_rho[n]) / m.compartment1_vis[n]) ** (2/3))))))
   m.eq21 = Constraint(m.i, m.n, rule=_eq21_rule)

   def _eq22_rule(m, i, n):
      return (m.compartment5_kL[i,n] == (m.compartment5_kL_discr[i] * (0.13 * ((((m.interface12_Pv[n] * m.compartment5_vis[n]) / (m.compartment5_rho[n] * m.compartment5_rho[n])) ** 0.25) * (((m.compartment5_D[n] * m.compartment5_rho[n]) / m.compartment5_vis[n]) ** (2/3))))))
   m.eq22 = Constraint(m.i, m.n, rule=_eq22_rule)

   def _eq23_rule(m, p, n):
      return (m.compartment5_k_aq[p,n] == (m.compartment5_k0_aq[p] * exp((((0 - m.compartment5_E_aq[p]) / 8.314) * ((1 / m.environment_Tc[n]) - (1 / m.compartment5_Tref_aq[p]))))))
   m.eq23 = Constraint(m.p, m.n, rule=_eq23_rule)

   def _eq24_rule(m, n):
      return (m.interface12_Pv[n] == ((0.2 * ((((1 - m.interface12_phi[n]) * m.compartment5_rho[n]) + (m.interface12_phi[n] * m.compartment1_rho[n])) * (((m.interface12_N / 60) ** 3) * (m.interface12_d ** 5)))) / ((m.compartment5_V + m.compartment1_V) * 1e-5)))
   m.eq24 = Constraint(m.n, rule=_eq24_rule)

   def _eq25_rule(m, n):
      return (m.compartment1_vis[n] == (0.0286 * exp(((-0.012) * m.environment_Tc[n]))))
   m.eq25 = Constraint(m.n, rule=_eq25_rule)

   def _eq26_rule(m, n):
      return (m.compartment5_rho[n] == ((-0.0039 * (m.environment_Tc[n] ** 2)) + ((2.0516 * m.environment_Tc[n]) + 727.52)))
   m.eq26 = Constraint(m.n, rule=_eq26_rule)

   def _eq27_rule(m, n):
      return (m.compartment5_D[n] == (0.0000000125 * (((m.compartment5_MVp ** (-0.19)) - 0.292) * ((m.environment_Tc[n] ** 1.52) * (m.compartment5_vis[n] ** m.compartment5_lD[n])))))
   m.eq27 = Constraint(m.n, rule=_eq27_rule)

   def _eq28_rule(m, n):
      return (m.compartment5_vis[n] == (0.2953 * exp(((-0.019) * m.environment_Tc[n]))))
   m.eq28 = Constraint(m.n, rule=_eq28_rule)

   def _eq29_rule(m, n):
      return (m.compartment1_rho[n] == ((-0.7889 * m.environment_Tc[n]) + 1075.8))
   m.eq29 = Constraint(m.n, rule=_eq29_rule)

   def _eq30_rule(m, n):
      return (m.compartment1_D[n] == (0.0000000155 * ((m.environment_Tc[n] ** 1.29) * ((m.compartment1_Pl ** 0.5) * ((m.compartment1_Pp ** (-0.42)) * ((m.compartment1_vis[n] ** -0.92) * (m.compartment1_MV ** (-0.23))))))))
   m.eq30 = Constraint(m.n, rule=_eq30_rule)

   def _eq31_rule(m, n):
      return (m.compartment5_lD[n] == ((0.958 / m.compartment5_MVp) - 1.12))
   m.eq31 = Constraint(m.n, rule=_eq31_rule)

   # End: Block 4

   # Set up list of pairs of measured vs. computed variables so that parmest can access them for the objective function
   m.measurement_pairs = []
   for index, var in enumerate(input_profile["measured_var"]):
      m.measurement_pairs.append((m.component(list(var.keys())[0]),input_profile["measured_var_index"][index][list(var.keys())[0]],m.component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas")))
   m.experiments = range(1,input_profile["n_exp"]+1)

   return m