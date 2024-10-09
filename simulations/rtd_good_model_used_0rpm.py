from pyomo.environ import *
from pyomo.dae import *
import pandas as pd
import matplotlib.pyplot as plt
import bisect

from tikzplotlib import save as tikz_save

from matplotlib.lines import Line2D
from matplotlib.legend import Legend
Line2D._us_dashSeq    = property(lambda self: self._dash_pattern[1])
Line2D._us_dashOffset = property(lambda self: self._dash_pattern[0])
Legend._ncol = property(lambda self: self._ncols)

def generate_input_profile(case_study) -> dict:
        
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

def generate_knownvals(input_profile):
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

def create_pyomo_model(input_profile):
     
   # Choose model class
   m = ConcreteModel()

   # Begin: Block 1
   # Create sets
   m.t = ContinuousSet(initialize=input_profile['sets']['t']['init_points'], bounds=(0,72))
   m.tau = RangeSet(0,15)
   # End: Block 1
   # Set up parameters for the measured experimental variables   
   m.tofMeas = Set(initialize=input_profile["sets"]["t"]["meas_points"])
   for index, var in enumerate(input_profile["measured_var"]):
      m.add_component(list(var.keys())[0]+"["+str(input_profile["measured_var_index"][index][list(var.keys())[0]])+"]_meas", Param(m.tofMeas, initialize=input_profile["measured_var"][index][list(var.keys())[0]]))

   # Begin: Block 2
   # Define parameters
   m.compartment14_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment4_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment1_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.interface24_V_dot_conv = Param(initialize=0.913444)
   m.interface24_c_conv = Var(m.t)
   def _inputfunc(m, t):
       if t == 0:
            return (m.interface24_c_conv[t] == 0.05)
       else:
            return (m.interface24_c_conv[t] == 0)
   m.inputfunc = Constraint(m.t, rule=_inputfunc)
   m.compartment15_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment18_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   m.compartment11_V = Var(bounds=(1e-06,20)) # This parameter is to be estimated.
   # End: Block 2

   # Begin: Block 3
   # Create variables
   m.interface33_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface19_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface14_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface19_c_conv = Var(m.t, bounds=(0,1))
   m.interface22_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface16_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface12_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface18_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface35_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface7_c_conv = Var(m.t, bounds=(0,1))
   m.interface22_c_conv = Var(m.t, bounds=(0,1))
   m.interface28_c_conv = Var(m.t, bounds=(0,1))
   m.interface7_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface10_c_conv = Var(m.t, bounds=(0,1))
   m.interface32_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface12_c_conv = Var(m.t, bounds=(0,1))
   m.compartment14_tau = Var(bounds=(0,20))
   m.interface18_c_conv = Var(m.t, bounds=(0,1))
   m.interface25_c_conv = Var(m.t, bounds=(0,1))
   m.interface23_c_conv = Var(m.t, bounds=(0,1))
   m.interface28_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface23_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface10_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface25_V_dot_conv = Var(bounds=(1e-06,1))
   m.interface32_c_conv = Var(m.t, bounds=(0,1))
   m.interface14_c_conv = Var(m.t, bounds=(0,1))
   m.interface34_c_conv = Var(m.t, bounds=(0,1))
   m.interface35_c_conv = Var(m.t, bounds=(0,1))
   m.interface16_c_conv = Var(m.t, bounds=(0,1))
   m.interface33_c_conv = Var(m.t, bounds=(0,1))
   m.interface34_V_dot_conv = Var(bounds=(1e-06,1))
   m.compartment14_xtau = Var(m.tau, bounds=(0,1), domain=Binary)
   m.compartment18_dcdt = DerivativeVar(m.interface32_c_conv, wrt=m.t)
   m.compartment15_dcdt = DerivativeVar(m.interface25_c_conv, wrt=m.t)
   m.compartment4_dcdt = DerivativeVar(m.interface7_c_conv, wrt=m.t)
   m.compartment11_dcdt = DerivativeVar(m.interface19_c_conv, wrt=m.t)
   m.compartment1_dcdt = DerivativeVar(m.interface10_c_conv, wrt=m.t)
   # End: Block 3

   # Begin: Block 4
   # Define equations
   def _eq1_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment1_V * m.compartment1_dcdt[t]) == ((m.interface7_c_conv[t] - m.interface10_c_conv[t]) * m.interface7_V_dot_conv))
   m.eq1 = Constraint(m.t, rule=_eq1_rule)

   def _eq2_rule(m):
      return (m.interface7_V_dot_conv == m.interface10_V_dot_conv)
   m.eq2 = Constraint(rule=_eq2_rule)

   def _eq3_rule(m):
      return (m.interface10_c_conv[0] == 0)
   m.eq3 = Constraint(rule=_eq3_rule)

   def _eq4_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment4_V * m.compartment4_dcdt[t]) == ((m.interface25_c_conv[t] - m.interface7_c_conv[t]) * m.interface25_V_dot_conv))
   m.eq4 = Constraint(m.t, rule=_eq4_rule)

   def _eq5_rule(m):
      return (m.interface25_V_dot_conv == m.interface7_V_dot_conv)
   m.eq5 = Constraint(rule=_eq5_rule)

   def _eq6_rule(m):
      return (m.interface7_c_conv[0] == 0)
   m.eq6 = Constraint(rule=_eq6_rule)

   def _eq7_rule(m, t):
      return (m.interface18_c_conv[t] == m.interface10_c_conv[t])
   m.eq7 = Constraint(m.t, rule=_eq7_rule)

   def _eq8_rule(m, t):
      return (m.interface12_c_conv[t] == m.interface10_c_conv[t])
   m.eq8 = Constraint(m.t, rule=_eq8_rule)

   def _eq9_rule(m):
      return (m.interface10_V_dot_conv == (m.interface18_V_dot_conv + m.interface12_V_dot_conv))
   m.eq9 = Constraint(rule=_eq9_rule)

   def _eq10_rule(m, t):
      return ((m.interface14_c_conv[t] * m.interface14_V_dot_conv) == ((m.interface19_c_conv[t] * m.interface19_V_dot_conv) + (m.interface12_c_conv[t] * m.interface12_V_dot_conv)))
   m.eq10 = Constraint(m.t, rule=_eq10_rule)

   def _eq11_rule(m):
      return (m.interface14_V_dot_conv == (m.interface19_V_dot_conv + m.interface12_V_dot_conv))
   m.eq11 = Constraint(rule=_eq11_rule)

   def _eq12_rule(m, t):
      return (m.interface22_c_conv[t] == m.interface14_c_conv[t])
   m.eq12 = Constraint(m.t, rule=_eq12_rule)

   def _eq13_rule(m, t):
      return (m.interface16_c_conv[t] == m.interface14_c_conv[t])
   m.eq13 = Constraint(m.t, rule=_eq13_rule)

   def _eq14_rule(m):
      return (m.interface14_V_dot_conv == (m.interface22_V_dot_conv + m.interface16_V_dot_conv))
   m.eq14 = Constraint(rule=_eq14_rule)

   def _eq15_rule(m, t):
      return ((m.interface28_c_conv[t] * m.interface28_V_dot_conv) == ((m.interface23_c_conv[t] * m.interface23_V_dot_conv) + (m.interface16_c_conv[t] * m.interface16_V_dot_conv)))
   m.eq15 = Constraint(m.t, rule=_eq15_rule)

   def _eq16_rule(m):
      return (m.interface28_V_dot_conv == (m.interface23_V_dot_conv + m.interface16_V_dot_conv))
   m.eq16 = Constraint(rule=_eq16_rule)

   def _eq17_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment11_V * m.compartment11_dcdt[t]) == ((m.interface18_c_conv[t] - m.interface19_c_conv[t]) * m.interface18_V_dot_conv))
   m.eq17 = Constraint(m.t, rule=_eq17_rule)

   def _eq18_rule(m):
      return (m.interface18_V_dot_conv == m.interface19_V_dot_conv)
   m.eq18 = Constraint(rule=_eq18_rule)

   def _eq19_rule(m):
      return (m.interface19_c_conv[0] == 0)
   m.eq19 = Constraint(rule=_eq19_rule)

   def _eq20_rule(m, t):
      return (m.interface23_c_conv[t] == sum((m.compartment14_xtau[tau] * m.interface22_c_conv[t - tau]) for tau in range(0,1+input_profile['sets']['tau']['max']) if t-tau >= 0))
   m.eq20 = Constraint(m.t, rule=_eq20_rule)

   def _eq21_rule(m):
      return (m.compartment14_V == (m.compartment14_tau * m.interface22_V_dot_conv))
   m.eq21 = Constraint(rule=_eq21_rule)

   def _eq22_rule(m):
      return (1 == sum(m.compartment14_xtau[tau] for tau in range(0,1+input_profile['sets']['tau']['max'])))
   m.eq22 = Constraint(rule=_eq22_rule)

   def _eq23_rule(m):
      return (m.compartment14_tau == sum(tau * m.compartment14_xtau[tau] for tau in range(0,1+input_profile['sets']['tau']['max'])))
   m.eq23 = Constraint(rule=_eq23_rule)

   def _eq24_rule(m):
      return (m.interface22_V_dot_conv == m.interface23_V_dot_conv)
   m.eq24 = Constraint(rule=_eq24_rule)

   def _eq25_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment15_V * m.compartment15_dcdt[t]) == ((m.interface24_c_conv[t] - m.interface25_c_conv[t]) * m.interface24_V_dot_conv))
   m.eq25 = Constraint(m.t, rule=_eq25_rule)

   def _eq26_rule(m):
      return (m.interface24_V_dot_conv == m.interface25_V_dot_conv)
   m.eq26 = Constraint(rule=_eq26_rule)

   def _eq27_rule(m):
      return (m.interface25_c_conv[0] == (m.interface24_c_conv[0] / m.compartment15_V))
   m.eq27 = Constraint(rule=_eq27_rule)

   def _eq28_rule(m, t):
      if t == 0:
            return Constraint.Skip
      return ((m.compartment18_V * m.compartment18_dcdt[t]) == ((m.interface28_c_conv[t] - m.interface32_c_conv[t]) * m.interface28_V_dot_conv))
   m.eq28 = Constraint(m.t, rule=_eq28_rule)

   def _eq29_rule(m):
      return (m.interface28_V_dot_conv == m.interface32_V_dot_conv)
   m.eq29 = Constraint(rule=_eq29_rule)

   def _eq30_rule(m):
      return (m.interface32_c_conv[0] == 0)
   m.eq30 = Constraint(rule=_eq30_rule)

   def _eq31_rule(m, t):
      return (m.interface33_c_conv[t] == m.interface32_c_conv[t])
   m.eq31 = Constraint(m.t, rule=_eq31_rule)

   def _eq32_rule(m, t):
      return (m.interface34_c_conv[t] == m.interface32_c_conv[t])
   m.eq32 = Constraint(m.t, rule=_eq32_rule)

   def _eq33_rule(m):
      return (m.interface32_V_dot_conv == (m.interface33_V_dot_conv + m.interface34_V_dot_conv))
   m.eq33 = Constraint(rule=_eq33_rule)

   def _eq34_rule(m, t):
      return ((m.interface35_c_conv[t] * m.interface35_V_dot_conv) == ((m.interface33_c_conv[t] * m.interface33_V_dot_conv) + (m.interface34_c_conv[t] * m.interface34_V_dot_conv)))
   m.eq34 = Constraint(m.t, rule=_eq34_rule)

   def _eq35_rule(m):
      return (m.interface35_V_dot_conv == (m.interface33_V_dot_conv + m.interface34_V_dot_conv))
   m.eq35 = Constraint(rule=_eq35_rule)

   def _eq36_rule(m):
      return (16 <= (m.compartment1_V + (m.compartment4_V + (m.compartment11_V + (m.compartment14_V + (m.compartment15_V + m.compartment18_V))))))
   m.eq36 = Constraint(rule=_eq36_rule)

   def _eq37_rule(m):
      return (19 >= (m.compartment1_V + (m.compartment4_V + (m.compartment11_V + (m.compartment14_V + (m.compartment15_V + m.compartment18_V))))))
   m.eq37 = Constraint(rule=_eq37_rule)

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
input_profile = generate_knownvals(input_profile)
base_model = create_pyomo_model(input_profile)

# Choose error function
def SSE(m):
   if any(i==999 for (var,i,var_meas) in m.measurement_pairs):
         var_expr = "var[n]"
   else:
         var_expr = "var[i,n]"
   expr = sum(
            (1/(0.0008)**2)*(eval(var_expr) - (var_meas[n]))**2
            # (1/(0.00088)**2)*(eval(var_expr) - (var_meas[n]))**2
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

plot_values["interface35_c_conv_meas[999]"] = list(input_profile["measured_var"][0]["interface35_c_conv"].values())

plt.plot(t_steps, plot_values["interface24_c_conv"], label="Tracer")
plt.legend()
# plt.show()

t_steps = [t*3.22392/60 for t in t_steps]
t_steps_meas = [t*3.22392/60 for t in t_steps_meas]

plot_values["interface35_c_conv"] = [c*1000 for c in plot_values["interface35_c_conv"]]
plot_values["interface35_c_conv_meas[999]"] = [c*1000 for c in plot_values["interface35_c_conv_meas[999]"]]

fig = plt.figure(figsize=(8, 8))

plt.plot(t_steps, plot_values["interface35_c_conv"], label="Simulated Outlet Concentration", color="green")
# plt.plot(t_steps, plot_values["interface25_c_conv"], label="After first CSTR")
# plt.plot(t_steps, plot_values["interface33_c_conv"], label="From CSTR")
# plt.plot(t_steps, plot_values["interface7_c_conv"], label="From CSTR")
# plt.plot(t_steps, plot_values["interface31_c_conv"], label="Out of C4")
# plt.plot(t_steps, plot_values["interface32_c_conv"], label="Out of C22")
plt.scatter(t_steps_meas, plot_values["interface35_c_conv_meas[999]"], label="Experimental Data", marker="x", color="red")
plt.legend()
plt.xlabel("Time (min)")
plt.ylabel("Concentration (mg/L)")
plt.grid(True)
plt.show()

## Bug workaround
# def tikzplotlib_fix_ncols(obj):
#    """
#    workaround for matplotlib 3.6 renamed legend's _ncol to _ncols, which breaks tikzplotlib
#    """
#    if hasattr(obj, "_ncols"):
#       obj.f_ncol = obj._ncols
#    for child in obj.get_children():
#       tikzplotlib_fix_ncols(child)

# tikzplotlib_fix_ncols(fig)

# tikz_save("./workflow/plotting_scripts/plot.tex")

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