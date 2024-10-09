from pyomo.environ import *
from pyomo.dae import *
import pandas as pd
import matplotlib.pyplot as plt
import bisect

def generate_input_profile(case_study) -> dict:
        
   # Name and index of measured variable
   measured_var = [{"target":"envflow2","variable":"c_conv","index":999}]

   manipulated_var = [{"target":"envflow1", "variable":"c_conv"}]

   n_exp = 24
   
   input_profile = {}
   input_profile["sets"] = {
         't':{'min': 0, 'max': 51, 'type': 'continuous', 'description': "indexes time"},
         'tau':{'min':0, 'max':15, 'type': 'discrete', 'description': "tau"}
         }
   
   input_profile["known_values"] = [
                  {"target":"envflow1", "variable":"V_dot_conv", "value":17/60},
                  ]

   input_data = pd.read_csv('./workflow/inputs/MB_MeCN_8.50ml_360rpm_rtd.csv', delimiter=";")

   input_profile["sets"]['t']['meas_points'] = []
   for set in input_profile["sets"].keys():
      if set in input_data.columns.values.tolist():
         input_profile["sets"][set]['meas_points'] = list({n: mani for n, mani in zip(range(1,n_exp+1), input_data[set].tolist())}.values())

   time_normalization_granularity = 3.235726/1

   input_profile["sets"]['t']['meas_points'] = [int(round(time/time_normalization_granularity,0)) for time in input_profile["sets"]['t']['meas_points']]

   input_profile["sets"]['t']['init_points'] = list(range(0,max(input_profile["sets"]['t']['meas_points'])+1))
   
   # Dummy, we use function here
   input_profile["manipulated_var"] = []
   for index, var in enumerate(manipulated_var):
      var["value"] = {n: mani for n, mani in zip(range(1,n_exp+1), input_data[manipulated_var[index]["variable"]].tolist())}
      input_profile["manipulated_var"].append(manipulated_var[index])

   def input_function(node):
      return (f"   def _inputfunc(m, t):\n" +
               f"       if t == 0:\n" +
               f"            return (m.{node.unique_representation}[t] == 0.176470588)\n" +
               f"       else:\n" +
               f"            return (m.{node.unique_representation}[t] == 0)\n" +
               f"   m.inputfunc = Constraint(m.t, rule=_inputfunc)\n"
               )
   
   input_profile["input_function"] = input_function

   input_profile["measured_var"] = []
   for index, var in enumerate(measured_var):
      var["value"] = {n: meas for n, meas in zip(input_profile["sets"]['t']['meas_points'], input_data[measured_var[index]["variable"]+"["+str(measured_var[index]["index"])+"]"].tolist())}
      input_profile["measured_var"].append(measured_var[index])

   # input_profile["measured_var"][0]["value"] = {key:input_profile["measured_var"][0]["value"][key]/(0.176470588/3.235726) for key in input_profile["measured_var"][0]["value"].keys()}

   input_profile["n_exp"] = n_exp

   return input_profile

def generate_input_profile_rasetest(case_study) -> dict:
        
   # Name and index of measured variable
   measured_var = [{"target":"envflow2","variable":"c_conv","index":999}]

   manipulated_var = [{"target":"envflow1", "variable":"c_conv"}]

   n_exp = 22
   
   input_profile = {}
   input_profile["sets"] = {
         't':{'min': 0, 'max': 72, 'type': 'continuous', 'description': "indexes time"},
         'tau':{'min':0, 'max':15, 'type': 'discrete', 'description': "tau"}
         }
   
   input_profile["known_values"] = [
                  {"target":"envflow1", "variable":"V_dot_conv", "value":17/60}, # not relevant here, see model
                  ]

   input_data = pd.read_csv('./workflow/inputs/MB_MeCN_8.50ml_0rpm_rtd.csv', delimiter=";")

   input_profile["sets"]['t']['meas_points'] = []
   for set in input_profile["sets"].keys():
      if set in input_data.columns.values.tolist():
         input_profile["sets"][set]['meas_points'] = list({n: mani for n, mani in zip(range(1,n_exp+1), input_data[set].tolist())}.values())

   time_normalization_granularity = 3.22392/1

   input_profile["sets"]['t']['meas_points'] = [int(round(time/time_normalization_granularity,0)) for time in input_profile["sets"]['t']['meas_points']]

   input_profile["sets"]['t']['init_points'] = list(range(0,max(input_profile["sets"]['t']['meas_points'])+1))
   
   # Dummy, we use function here
   input_profile["manipulated_var"] = []
   for index, var in enumerate(manipulated_var):
      var["value"] = {n: mani for n, mani in zip(range(1,n_exp+1), input_data[manipulated_var[index]["variable"]].tolist())}
      input_profile["manipulated_var"].append(manipulated_var[index])

   def input_function(node):
      return (f"   def _inputfunc(m, t):\n" +
               f"       if t == 0:\n" +
               f"            return (m.{node.unique_representation}[t] == 0.176470588)\n" +
               f"       else:\n" +
               f"            return (m.{node.unique_representation}[t] == 0)\n" +
               f"   m.inputfunc = Constraint(m.t, rule=_inputfunc)\n"
               )
   
   input_profile["input_function"] = input_function

   input_profile["measured_var"] = []
   for index, var in enumerate(measured_var):
      var["value"] = {n: meas for n, meas in zip(input_profile["sets"]['t']['meas_points'], input_data[measured_var[index]["variable"]+"["+str(measured_var[index]["index"])+"]"].tolist())}
      input_profile["measured_var"].append(measured_var[index])

   # input_profile["measured_var"][0]["value"] = {key:input_profile["measured_var"][0]["value"][key]/(0.176470588/3.235726) for key in input_profile["measured_var"][0]["value"].keys()}

   input_profile["n_exp"] = n_exp

   return input_profile

def generate_knownvals_rasetest(input_profile):
   # rename this to input_profile to avoid confusion
   known_values = {}
   
   known_values["measured_var"] = []
   known_values["measured_var_index"] = []
   for var in input_profile["measured_var"]:
      if var["target"] == "envflow2":
         var["target"] = "interface35"
      known_values["measured_var"].append({var["target"] + "_" + var["variable"]:var["value"]})
      known_values["measured_var_index"].append({var["target"] + "_" + var["variable"]:var["index"]})

      known_values["manipulated_var"] = []
      for var in input_profile["manipulated_var"]:
         if var["target"] == "envflow1":
            var["target"] = "interface24"
         known_values["manipulated_var"].append({var["target"] + "_" + var["variable"]:var["value"]})
   
   known_values["sets"] = input_profile["sets"]
   known_values["n_exp"] = input_profile["n_exp"]

   return known_values

def generate_knownvals(input_profile):
   # rename this to input_profile to avoid confusion
   known_values = {}
   
   known_values["measured_var"] = []
   known_values["measured_var_index"] = []
   for var in input_profile["measured_var"]:
      if var["target"] == "envflow2":
         var["target"] = "interface13"
      known_values["measured_var"].append({var["target"] + "_" + var["variable"]:var["value"]})
      known_values["measured_var_index"].append({var["target"] + "_" + var["variable"]:var["index"]})

      known_values["manipulated_var"] = []
      for var in input_profile["manipulated_var"]:
         if var["target"] == "envflow1":
            var["target"] = "interface26"
         known_values["manipulated_var"].append({var["target"] + "_" + var["variable"]:var["value"]})
   
   known_values["sets"] = input_profile["sets"]
   known_values["n_exp"] = input_profile["n_exp"]

   return known_values

def create_pyomo_model(input_profile):
     
   # Choose model class
   m = ConcreteModel()

   # Begin: Block 1
   # Create sets
   m.tau = RangeSet(0,15)
   m.t = ContinuousSet(initialize=input_profile['sets']['t']['init_points'], bounds=(0,29))
   # End: Block 1
   # Set up parameters for the measured experimental variables   
   m.tofMeas = Set(initialize=input_profile["sets"]["t"]["meas_points"])
   for index, var in enumerate(input_profile["measured_var"]):
      m.add_component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas", Param(m.tofMeas, initialize=input_profile["measured_var"][index][list(var.keys())[0]]))

   ### RASE TEST
   # # Begin: Block 1
   # # Create sets
   # m.t = ContinuousSet(initialize=input_profile['sets']['t']['init_points'], bounds=(0,72))
   # m.tau = RangeSet(0,15)
   # # End: Block 1
   # # Set up parameters for the measured experimental variables   
   # m.tofMeas = Set(initialize=input_profile["sets"]["t"]["meas_points"])
   # for index, var in enumerate(input_profile["measured_var"]):
   #    m.add_component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas", Param(m.tofMeas, initialize=input_profile["measured_var"][index][list(var.keys())[0]]))


   # Begin: Block 2
   # Define parameters
   m.compartment30_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment16_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment19_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment41_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.interface26_c_conv = Var(m.t)
   def _inputfunc(m, t):
       if t == 0:
            return (m.interface26_c_conv[t] == 0.035)
            # return (m.interface26_c_conv[t] == 0.05) # RASE TEST
       else:
            return (m.interface26_c_conv[t] == 0)
   m.inputfunc = Constraint(m.t, rule=_inputfunc)
   m.compartment44_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment1_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment13_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment22_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment33_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment36_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment8_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.interface26_V_dot_conv = Param(initialize=0.9167890333333334)
   m.compartment25_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.interface31_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface62_c_conv = Var(m.t, bounds=(0,1))
   m.interface46_c_conv = Var(m.t, bounds=(0,1))
   m.interface50_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface42_c_conv = Var(m.t, bounds=(0,1))
   m.interface48_c_conv = Var(m.t, bounds=(0,1))
   m.interface61_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface30_c_conv = Var(m.t, bounds=(0,1))
   m.interface64_c_conv = Var(m.t, bounds=(0,1))
   m.interface51_c_conv = Var(m.t, bounds=(0,1))
   m.interface57_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface43_c_conv = Var(m.t, bounds=(0,1))
   m.interface42_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface20_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface56_c_conv = Var(m.t, bounds=(0,1))
   m.interface18_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface57_c_conv = Var(m.t, bounds=(0,1))
   m.compartment30_xtau = Var(m.tau, bounds=(0,1), domain=Binary)
   m.interface65_c_conv = Var(m.t, bounds=(0,1))
   m.interface18_c_conv = Var(m.t, bounds=(0,1))
   m.interface47_c_conv = Var(m.t, bounds=(0,1))
   m.interface60_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface48_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface13_c_conv = Var(m.t, bounds=(0,1))
   m.interface38_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface12_c_conv = Var(m.t, bounds=(0,1))
   m.interface20_c_conv = Var(m.t, bounds=(0,1))
   m.interface64_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface53_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface50_c_conv = Var(m.t, bounds=(0,1))
   m.interface49_c_conv = Var(m.t, bounds=(0,1))
   m.interface34_c_conv = Var(m.t, bounds=(0,1))
   m.interface63_c_conv = Var(m.t, bounds=(0,1))
   m.interface31_c_conv = Var(m.t, bounds=(0,1))
   m.interface35_c_conv = Var(m.t, bounds=(0,1))
   m.interface52_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface62_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface12_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface47_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface30_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface56_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface46_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface34_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface35_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface60_c_conv = Var(m.t, bounds=(0,1))
   m.interface38_c_conv = Var(m.t, bounds=(0,1))
   m.interface69_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface65_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface49_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface43_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface51_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface68_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface13_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface39_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface39_c_conv = Var(m.t, bounds=(0,1))
   m.interface68_c_conv = Var(m.t, bounds=(0,1))
   m.interface69_c_conv = Var(m.t, bounds=(0,1))
   m.interface63_V_dot_conv = Var(bounds=(1e-06,1))
   m.compartment30_tau = Var(bounds=(0,20))
   m.interface61_c_conv = Var(m.t, bounds=(0,1))
   m.interface53_c_conv = Var(m.t, bounds=(0,1))
   m.interface52_c_conv = Var(m.t, bounds=(0,1))
   m.compartment33_dcdt = DerivativeVar(m.interface53_c_conv, wrt=m.t)
   m.compartment8_dcdt = DerivativeVar(m.interface34_c_conv, wrt=m.t)
   m.compartment1_dcdt = DerivativeVar(m.interface18_c_conv, wrt=m.t)
   m.compartment19_dcdt = DerivativeVar(m.interface31_c_conv, wrt=m.t)
   m.compartment41_dcdt = DerivativeVar(m.interface65_c_conv, wrt=m.t)
   m.compartment25_dcdt = DerivativeVar(m.interface39_c_conv, wrt=m.t)
   m.compartment22_dcdt = DerivativeVar(m.interface35_c_conv, wrt=m.t)
   m.compartment36_dcdt = DerivativeVar(m.interface57_c_conv, wrt=m.t)
   m.compartment44_dcdt = DerivativeVar(m.interface69_c_conv, wrt=m.t)
   m.compartment16_dcdt = DerivativeVar(m.interface56_c_conv, wrt=m.t)
   m.compartment13_dcdt = DerivativeVar(m.interface42_c_conv, wrt=m.t)
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment1_V * m.compartment1_dcdt[t]) == ((m.interface47_c_conv[t] - m.interface18_c_conv[t]) * m.interface47_V_dot_conv))
   m.eq1 = Constraint(m.t, rule=_eq1_rule)

   def _eq2_rule(m):
      return (m.interface47_V_dot_conv == m.interface18_V_dot_conv)
   m.eq2 = Constraint(rule=_eq2_rule)

   def _eq3_rule(m):
      return (m.interface18_c_conv[0] == 0)
   m.eq3 = Constraint(rule=_eq3_rule)

   def _eq4_rule(m, t):
      return (m.interface60_c_conv[t] == m.interface53_c_conv[t])
   m.eq4 = Constraint(m.t, rule=_eq4_rule)

   def _eq5_rule(m, t):
      return (m.interface48_c_conv[t] == m.interface53_c_conv[t])
   m.eq5 = Constraint(m.t, rule=_eq5_rule)

   def _eq6_rule(m):
      return (m.interface53_V_dot_conv == (m.interface60_V_dot_conv + m.interface48_V_dot_conv))
   m.eq6 = Constraint(rule=_eq6_rule)

   def _eq7_rule(m, t):
      return ((m.interface46_c_conv[t] * m.interface46_V_dot_conv) == ((m.interface63_c_conv[t] * m.interface63_V_dot_conv) + (m.interface35_c_conv[t] * m.interface35_V_dot_conv)))
   m.eq7 = Constraint(m.t, rule=_eq7_rule)

   def _eq8_rule(m):
      return (m.interface46_V_dot_conv == (m.interface63_V_dot_conv + m.interface35_V_dot_conv))
   m.eq8 = Constraint(rule=_eq8_rule)

   def _eq9_rule(m, t):
      return (m.interface64_c_conv[t] == m.interface31_c_conv[t])
   m.eq9 = Constraint(m.t, rule=_eq9_rule)

   def _eq10_rule(m, t):
      return (m.interface12_c_conv[t] == m.interface31_c_conv[t])
   m.eq10 = Constraint(m.t, rule=_eq10_rule)

   def _eq11_rule(m):
      return (m.interface31_V_dot_conv == (m.interface64_V_dot_conv + m.interface12_V_dot_conv))
   m.eq11 = Constraint(rule=_eq11_rule)

   def _eq12_rule(m, t):
      return ((m.interface13_c_conv[t] * m.interface13_V_dot_conv) == ((m.interface65_c_conv[t] * m.interface65_V_dot_conv) + (m.interface12_c_conv[t] * m.interface12_V_dot_conv)))
   m.eq12 = Constraint(m.t, rule=_eq12_rule)

   def _eq13_rule(m):
      return (m.interface13_V_dot_conv == (m.interface65_V_dot_conv + m.interface12_V_dot_conv))
   m.eq13 = Constraint(rule=_eq13_rule)

   def _eq14_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment8_V * m.compartment8_dcdt[t]) == ((m.interface51_c_conv[t] - m.interface34_c_conv[t]) * m.interface51_V_dot_conv))
   m.eq14 = Constraint(m.t, rule=_eq14_rule)

   def _eq15_rule(m):
      return (m.interface51_V_dot_conv == m.interface34_V_dot_conv)
   m.eq15 = Constraint(rule=_eq15_rule)

   def _eq16_rule(m):
      return (m.interface34_c_conv[0] == 0)
   m.eq16 = Constraint(rule=_eq16_rule)

   def _eq17_rule(m, t):
      return (m.interface38_c_conv[t] == m.interface18_c_conv[t])
   m.eq17 = Constraint(m.t, rule=_eq17_rule)

   def _eq18_rule(m, t):
      return (m.interface20_c_conv[t] == m.interface18_c_conv[t])
   m.eq18 = Constraint(m.t, rule=_eq18_rule)

   def _eq19_rule(m):
      return (m.interface18_V_dot_conv == (m.interface38_V_dot_conv + m.interface20_V_dot_conv))
   m.eq19 = Constraint(rule=_eq19_rule)

   def _eq20_rule(m, t):
      return ((m.interface30_c_conv[t] * m.interface30_V_dot_conv) == ((m.interface39_c_conv[t] * m.interface39_V_dot_conv) + (m.interface20_c_conv[t] * m.interface20_V_dot_conv)))
   m.eq20 = Constraint(m.t, rule=_eq20_rule)

   def _eq21_rule(m):
      return (m.interface30_V_dot_conv == (m.interface39_V_dot_conv + m.interface20_V_dot_conv))
   m.eq21 = Constraint(rule=_eq21_rule)

   def _eq22_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment13_V * m.compartment13_dcdt[t]) == ((m.interface57_c_conv[t] - m.interface42_c_conv[t]) * m.interface57_V_dot_conv))
   m.eq22 = Constraint(m.t, rule=_eq22_rule)

   def _eq23_rule(m):
      return (m.interface57_V_dot_conv == m.interface42_V_dot_conv)
   m.eq23 = Constraint(rule=_eq23_rule)

   def _eq24_rule(m):
      return (m.interface42_c_conv[0] == 0)
   m.eq24 = Constraint(rule=_eq24_rule)

   def _eq25_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment16_V * m.compartment16_dcdt[t]) == ((m.interface26_c_conv[t] - m.interface56_c_conv[t]) * m.interface26_V_dot_conv))
   m.eq25 = Constraint(m.t, rule=_eq25_rule)

   def _eq26_rule(m):
      return (m.interface26_V_dot_conv == m.interface56_V_dot_conv)
   m.eq26 = Constraint(rule=_eq26_rule)

   def _eq27_rule(m):
      return (m.interface56_c_conv[0] == (m.interface26_c_conv[0] / m.compartment16_V))
   m.eq27 = Constraint(rule=_eq27_rule)

   def _eq28_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment19_V * m.compartment19_dcdt[t]) == ((m.interface30_c_conv[t] - m.interface31_c_conv[t]) * m.interface30_V_dot_conv))
   m.eq28 = Constraint(m.t, rule=_eq28_rule)

   def _eq29_rule(m):
      return (m.interface30_V_dot_conv == m.interface31_V_dot_conv)
   m.eq29 = Constraint(rule=_eq29_rule)

   def _eq30_rule(m):
      return (m.interface31_c_conv[0] == 0)
   m.eq30 = Constraint(rule=_eq30_rule)

   def _eq31_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment22_V * m.compartment22_dcdt[t]) == ((m.interface34_c_conv[t] - m.interface35_c_conv[t]) * m.interface34_V_dot_conv))
   m.eq31 = Constraint(m.t, rule=_eq31_rule)

   def _eq32_rule(m):
      return (m.interface34_V_dot_conv == m.interface35_V_dot_conv)
   m.eq32 = Constraint(rule=_eq32_rule)

   def _eq33_rule(m):
      return (m.interface35_c_conv[0] == 0)
   m.eq33 = Constraint(rule=_eq33_rule)

   def _eq34_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment25_V * m.compartment25_dcdt[t]) == ((m.interface38_c_conv[t] - m.interface39_c_conv[t]) * m.interface38_V_dot_conv))
   m.eq34 = Constraint(m.t, rule=_eq34_rule)

   def _eq35_rule(m):
      return (m.interface38_V_dot_conv == m.interface39_V_dot_conv)
   m.eq35 = Constraint(rule=_eq35_rule)

   def _eq36_rule(m):
      return (m.interface39_c_conv[0] == 0)
   m.eq36 = Constraint(rule=_eq36_rule)

   def _eq37_rule(m, t):
      return (m.interface43_c_conv[t] == m.interface42_c_conv[t])
   m.eq37 = Constraint(m.t, rule=_eq37_rule)

   def _eq38_rule(m, t):
      return (m.interface68_c_conv[t] == m.interface42_c_conv[t])
   m.eq38 = Constraint(m.t, rule=_eq38_rule)

   def _eq39_rule(m):
      return (m.interface42_V_dot_conv == (m.interface43_V_dot_conv + m.interface68_V_dot_conv))
   m.eq39 = Constraint(rule=_eq39_rule)

   def _eq40_rule(m, t):
      return ((m.interface52_c_conv[t] * m.interface52_V_dot_conv) == ((m.interface43_c_conv[t] * m.interface43_V_dot_conv) + (m.interface69_c_conv[t] * m.interface69_V_dot_conv)))
   m.eq40 = Constraint(m.t, rule=_eq40_rule)

   def _eq41_rule(m):
      return (m.interface52_V_dot_conv == (m.interface43_V_dot_conv + m.interface69_V_dot_conv))
   m.eq41 = Constraint(rule=_eq41_rule)

   def _eq42_rule(m, t):
      return (m.interface47_c_conv[t] == sum((m.compartment30_xtau[tau] * m.interface46_c_conv[t - tau]) for tau in range(0,1+input_profile['sets']['tau']['max']) if t-tau >= 0))
   m.eq42 = Constraint(m.t, rule=_eq42_rule)

   def _eq43_rule(m):
      return (m.compartment30_V == (m.compartment30_tau * m.interface46_V_dot_conv))
   m.eq43 = Constraint(rule=_eq43_rule)

   def _eq44_rule(m):
      return (1 == sum(m.compartment30_xtau[tau] for tau in range(0,1+input_profile['sets']['tau']['max'])))
   m.eq44 = Constraint(rule=_eq44_rule)

   def _eq45_rule(m):
      return (m.compartment30_tau == sum(tau * m.compartment30_xtau[tau] for tau in range(0,1+input_profile['sets']['tau']['max'])))
   m.eq45 = Constraint(rule=_eq45_rule)

   def _eq46_rule(m):
      return (m.interface46_V_dot_conv == m.interface47_V_dot_conv)
   m.eq46 = Constraint(rule=_eq46_rule)

   def _eq47_rule(m, t):
      return (m.interface49_c_conv[t] == m.interface48_c_conv[t])
   m.eq47 = Constraint(m.t, rule=_eq47_rule)

   def _eq48_rule(m, t):
      return (m.interface50_c_conv[t] == m.interface48_c_conv[t])
   m.eq48 = Constraint(m.t, rule=_eq48_rule)

   def _eq49_rule(m):
      return (m.interface48_V_dot_conv == (m.interface49_V_dot_conv + m.interface50_V_dot_conv))
   m.eq49 = Constraint(rule=_eq49_rule)

   def _eq50_rule(m, t):
      return ((m.interface51_c_conv[t] * m.interface51_V_dot_conv) == ((m.interface49_c_conv[t] * m.interface49_V_dot_conv) + (m.interface50_c_conv[t] * m.interface50_V_dot_conv)))
   m.eq50 = Constraint(m.t, rule=_eq50_rule)

   def _eq51_rule(m):
      return (m.interface51_V_dot_conv == (m.interface49_V_dot_conv + m.interface50_V_dot_conv))
   m.eq51 = Constraint(rule=_eq51_rule)

   def _eq52_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment33_V * m.compartment33_dcdt[t]) == ((m.interface52_c_conv[t] - m.interface53_c_conv[t]) * m.interface52_V_dot_conv))
   m.eq52 = Constraint(m.t, rule=_eq52_rule)

   def _eq53_rule(m):
      return (m.interface52_V_dot_conv == m.interface53_V_dot_conv)
   m.eq53 = Constraint(rule=_eq53_rule)

   def _eq54_rule(m):
      return (m.interface53_c_conv[0] == 0)
   m.eq54 = Constraint(rule=_eq54_rule)

   def _eq55_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment36_V * m.compartment36_dcdt[t]) == ((m.interface56_c_conv[t] - m.interface57_c_conv[t]) * m.interface56_V_dot_conv))
   m.eq55 = Constraint(m.t, rule=_eq55_rule)

   def _eq56_rule(m):
      return (m.interface56_V_dot_conv == m.interface57_V_dot_conv)
   m.eq56 = Constraint(rule=_eq56_rule)

   def _eq57_rule(m):
      return (m.interface57_c_conv[0] == 0)
   m.eq57 = Constraint(rule=_eq57_rule)

   def _eq58_rule(m, t):
      return (m.interface61_c_conv[t] == m.interface60_c_conv[t])
   m.eq58 = Constraint(m.t, rule=_eq58_rule)

   def _eq59_rule(m, t):
      return (m.interface62_c_conv[t] == m.interface60_c_conv[t])
   m.eq59 = Constraint(m.t, rule=_eq59_rule)

   def _eq60_rule(m):
      return (m.interface60_V_dot_conv == (m.interface61_V_dot_conv + m.interface62_V_dot_conv))
   m.eq60 = Constraint(rule=_eq60_rule)

   def _eq61_rule(m, t):
      return ((m.interface63_c_conv[t] * m.interface63_V_dot_conv) == ((m.interface61_c_conv[t] * m.interface61_V_dot_conv) + (m.interface62_c_conv[t] * m.interface62_V_dot_conv)))
   m.eq61 = Constraint(m.t, rule=_eq61_rule)

   def _eq62_rule(m):
      return (m.interface63_V_dot_conv == (m.interface61_V_dot_conv + m.interface62_V_dot_conv))
   m.eq62 = Constraint(rule=_eq62_rule)

   def _eq63_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment41_V * m.compartment41_dcdt[t]) == ((m.interface64_c_conv[t] - m.interface65_c_conv[t]) * m.interface64_V_dot_conv))
   m.eq63 = Constraint(m.t, rule=_eq63_rule)

   def _eq64_rule(m):
      return (m.interface64_V_dot_conv == m.interface65_V_dot_conv)
   m.eq64 = Constraint(rule=_eq64_rule)

   def _eq65_rule(m):
      return (m.interface65_c_conv[0] == 0)
   m.eq65 = Constraint(rule=_eq65_rule)

   def _eq66_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment44_V * m.compartment44_dcdt[t]) == ((m.interface68_c_conv[t] - m.interface69_c_conv[t]) * m.interface68_V_dot_conv))
   m.eq66 = Constraint(m.t, rule=_eq66_rule)

   def _eq67_rule(m):
      return (m.interface68_V_dot_conv == m.interface69_V_dot_conv)
   m.eq67 = Constraint(rule=_eq67_rule)

   def _eq68_rule(m):
      return (m.interface69_c_conv[0] == 0)
   m.eq68 = Constraint(rule=_eq68_rule)

   def _eq69_rule(m):
      return (16 <= (m.compartment1_V + (m.compartment8_V + (m.compartment13_V + (m.compartment16_V + (m.compartment19_V + (m.compartment22_V + (m.compartment25_V + (m.compartment30_V + (m.compartment33_V + (m.compartment36_V + (m.compartment41_V + m.compartment44_V))))))))))))
   m.eq69 = Constraint(rule=_eq69_rule)

   def _eq70_rule(m):
      return (19 >= (m.compartment1_V + (m.compartment8_V + (m.compartment13_V + (m.compartment16_V + (m.compartment19_V + (m.compartment22_V + (m.compartment25_V + (m.compartment30_V + (m.compartment33_V + (m.compartment36_V + (m.compartment41_V + m.compartment44_V))))))))))))
   m.eq70 = Constraint(rule=_eq70_rule)

   # End: Block 4

   discretizer = TransformationFactory('dae.finite_difference')
   discretizer.apply_to(m,nfe=input_profile["n_exp"],wrt=m.t,scheme='BACKWARD')

   # Set up list of pairs of measured vs. computed variables so that parmest can access them for the objective function
   m.measurement_pairs = []
   for index, var in enumerate(input_profile["measured_var"]):
      m.measurement_pairs.append((m.component(list(var.keys())[0]),input_profile["measured_var_index"][index][list(var.keys())[0]],m.component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas")))
   m.experiments = range(1,input_profile["n_exp"]+1)

   return m

input_profile = generate_input_profile("tcr-rtd")
# input_profile = generate_input_profile_rasetest("tcr-rtd")

input_profile = generate_knownvals(input_profile)
base_model = create_pyomo_model(input_profile)

# Choose error function
def SSE(m):
   if any(i==999 for (var,i,var_meas) in m.measurement_pairs):
         var_expr = "var[n]"
   else:
         var_expr = "var[i,n]"
   expr = sum(
            # (1/(0.0008/(0.176470588/3.235726))**2)*(eval(var_expr) - (var_meas[n]))**2
            (1/(0.0008)**2)*(eval(var_expr) - (var_meas[n]))**2
            # (1000*eval(var_expr) - (1000*var_meas[n]))**2
            # (eval(var_expr) - (var_meas[n]))**2
            for (var,i,var_meas) in m.measurement_pairs
            # for n in m.experiments
            for n in var_meas.index_set()
            )
   return expr

base_model.obj = Objective(rule=SSE, sense=minimize)

# Output
import sys
f = open('.\debug-pyomomodel.txt', 'w')
standard = sys.stdout
sys.stdout = f
base_model.pprint()
sys.stdout = standard

report = pyomo.util.model_size.build_model_size_report(base_model)
print("Num constraints: ", report.activated.constraints)
print("Num variables: ", report.activated.variables)

io_options = dict(
            # add_options=['GAMS_MODEL.optfile = 1;','$onecho > ipopt.opt', 'tol 1e-4\n', '$offecho'], 
            add_options=['GAMS_MODEL.optfile = 1;','$onecho > dicopt.opt', '\n stop 0\n', '$offecho'], 
            # add_options=['GAMS_MODEL.optfile = 1;','$onecho > baron.opt', 'reslim 30\n  NumLoc 30\n Threads 8\n', '$offecho'], 
            )


solver = SolverFactory('gams')
try:
   results = solver.solve(base_model, solver='dicopt', keepfiles=True, tee=True, io_options=io_options)
except:
   results = solver.solve(base_model, solver='ipopt', keepfiles=True, tee=True, io_options=io_options)


if results.solver.termination_condition == TerminationCondition.maxTimeLimit:
      obj = results["Solver"][0]["Primal bound"]

t_steps_meas = input_profile["sets"]["t"]["meas_points"]

# t_steps = input_profile["sets"]["t"]["init_points"]
t_steps = list(base_model.t)

var_values = {}
plot_values = {}
for v in base_model.component_objects(Var, active=True):
   if "V" in str(v) or "V_dot" in str(v) or "tau" in str(v):
      var_object = getattr(base_model, str(v))
      for index in var_object:
         var_values[str(v) + str(index)] = var_object[index].value
   if "interface" in str(v) and "c_conv" in str(v):
      var_object = getattr(base_model, str(v))
      plot_values[str(v)] = [var_object[index].value for index in t_steps]

plot_values["interface13_c_conv_meas[999]"] = list(input_profile["measured_var"][0]["interface13_c_conv"].values())

plt.plot(t_steps, plot_values["interface26_c_conv"], label="Tracer")
plt.legend()
plt.show()

t_steps = [t/3.235726 for t in t_steps]
t_steps_meas = [t/3.235726 for t in t_steps_meas]

plt.plot(t_steps, plot_values["interface13_c_conv"], label="Simulated Outlet Concentration")
# plt.plot(t_steps, plot_values["interface25_c_conv"], label="After first CSTR")
# plt.plot(t_steps, plot_values["interface33_c_conv"], label="From CSTR")
# plt.plot(t_steps, plot_values["interface7_c_conv"], label="From CSTR")
# plt.plot(t_steps, plot_values["interface31_c_conv"], label="Out of C4")
# plt.plot(t_steps, plot_values["interface32_c_conv"], label="Out of C22")
plt.scatter(t_steps_meas, plot_values["interface13_c_conv_meas[999]"], label="Experimental Data", marker="x")
plt.legend()
plt.xlabel("Time ()")
plt.grid(True)
plt.show()

# import numpy as np

# # Example lists
# x = t_steps_meas
# y = plot_values["interface21_c_conv_meas[999]"]

# # Ensure lists are numpy arrays
# x = np.array(x)
# y = np.array(y)

# # Perform the integration using the trapezoidal rule
# integral = np.trapz(y, x)

# print(f"The integral of y over x is: {integral}")

print("")