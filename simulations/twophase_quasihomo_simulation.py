import pyomo.dae as dae
import pyomo.environ as pyo
from pyomo.util.model_size import build_model_size_report
import matplotlib.pyplot as plt
import numpy as np

V_dot_aqs = [1.2748e-5] * 130 #m3/s
V_dot_orgs = [1.65e-5] * 130 #m3/s
Tcs = range(290,420,1)
V_totals = [0.105] * 130 #m3
c_product_epox = []
c_educt_limo = []
kL_aq = []
kL_org = []

for i, dummy in enumerate(V_totals):
    print(i)
    m = pyo.ConcreteModel()

    m.i = pyo.Set(initialize=["CAT","H2O2","ACAT","H2O","LIMO","EPOX"])

    m.c_out = pyo.Var(m.i, bounds=(0,100))
    m.c_in = pyo.Param(m.i, initialize={"CAT":0.0348,"H2O2":4.302,"ACAT":0,"H2O":18.603,"LIMO":4.604,"EPOX":0})
    m.V_dot_aq = pyo.Param(initialize=V_dot_aqs[i])
    m.V_dot_org = pyo.Param(initialize=V_dot_orgs[i])
    m.V_aq = pyo.Var(bounds=(0,1))
    m.V_org = pyo.Var(bounds=(0,1))

    m.V_total = pyo.Param(initialize=V_totals[i])
    m.phi = pyo.Var(bounds=(0,1))

    m.r_aq_i = pyo.Var(m.i, bounds=(-1,1))
    m.r_aq_i["LIMO"].fix(0)
    m.r_aq_i["EPOX"].fix(0)
    m.r_aq = pyo.Var(bounds=(0,1))
    m.k_aq = pyo.Var(bounds=(0,20))

    m.r_org_i = pyo.Var(m.i, bounds=(-1,1))
    m.r_org_i["H2O2"].fix(0)
    m.r_org_i["H2O"].fix(0)
    m.r_org = pyo.Var(bounds=(0,1))
    m.k_org = pyo.Var(bounds=(0,20))

    m.eps = pyo.Param(initialize=1e-22)

    m.Tc = pyo.Param(initialize=Tcs[i]) # K

    m.k_aq0 = pyo.Param(initialize=0.0126092)
    m.k_org0 = pyo.Param(initialize=0.1)
    m.E_aq = pyo.Param(initialize=70111)
    m.E_org = pyo.Param(initialize=43024.2)
    m.R = pyo.Param(initialize=8.314)
    m.Tref = pyo.Param(initialize=317.3)

    def _volume_balance(m):
        return (m.V_total == m.V_aq + m.V_org)
    m._volume_balance = pyo.Constraint(rule=_volume_balance)

    def _phase_split1(m):
        return (m.phi == m.V_dot_org / (m.V_dot_aq + m.V_dot_org))
    m._phase_split1 = pyo.Constraint(rule=_phase_split1)

    def _phase_split2(m):
        return (m.phi == m.V_org / m.V_total)
    m._phase_split2 = pyo.Constraint(rule=_phase_split2)

    def _balance(m, i):
        return (0 == (m.c_in[i] - m.c_out[i]) * (m.V_dot_aq + m.V_dot_org) + m.V_total * m.r_aq_i[i] + m.V_total * m.r_org_i[i])
    m.balance = pyo.Constraint(m.i, rule=_balance)
    
    def _ratelaw_aq(m):
        return m.r_aq == m.k_aq * m.c_out["CAT"] * m.c_out["H2O2"]
    m.ratelaw_aq = pyo.Constraint(rule=_ratelaw_aq)

    def _ratelaw_org(m):
        return m.r_org == m.k_org * m.c_out["ACAT"] * m.c_out["LIMO"]
    m.ratelaw_org = pyo.Constraint(rule=_ratelaw_org)

    def _stoich_org_ACAT(m):
        return m.r_org_i["ACAT"] == -m.r_org
    m.stoich_org_ACAT = pyo.Constraint(rule=_stoich_org_ACAT)

    def _stoich_org_LIMO(m):
        return m.r_org_i["LIMO"] == -m.r_org
    m.stoich_org_LIMO = pyo.Constraint(rule=_stoich_org_LIMO)

    def _stoich_org_CAT(m):
        return m.r_org_i["CAT"] == m.r_org
    m.stoich_org_CAT = pyo.Constraint(rule=_stoich_org_CAT)

    def _stoich_org_EPOX(m):
        return m.r_org_i["EPOX"] == m.r_org
    m.stoich_org_EPOX = pyo.Constraint(rule=_stoich_org_EPOX)

    def _stoich_aq_ACAT(m):
        return m.r_aq_i["ACAT"] == m.r_aq
    m.stoich_aq_ACAT = pyo.Constraint(rule=_stoich_aq_ACAT)

    def _stoich_aq_CAT(m):
        return m.r_aq_i["CAT"] == -m.r_aq
    m.stoich_aq_CAT = pyo.Constraint(rule=_stoich_aq_CAT)

    def _stoich_aq_H2O2(m):
        return m.r_aq_i["H2O2"] == -m.r_aq
    m.stoich_aq_H2O2 = pyo.Constraint(rule=_stoich_aq_H2O2)

    def _stoich_aq_H2O(m):
        return m.r_aq_i["H2O"] == m.r_aq
    m.stoich_aq_H2O = pyo.Constraint(rule=_stoich_aq_H2O)

    def _arrhenius_aq(m):
        return m.k_aq == m.k_aq0 * pyo.exp(-m.E_aq / m.R * (1/m.Tc - 1/m.Tref))
    m.arrhenius_aq = pyo.Constraint(rule=_arrhenius_aq)
    
    def _arrhenius_org(m):
        return m.k_org == m.k_org0 * pyo.exp(-m.E_org / m.R * (1/m.Tc - 1/m.Tref))
    m.arrhenius_org = pyo.Constraint(rule=_arrhenius_org)

    m.obj = pyo.Objective(rule=1, sense=pyo.minimize)

    # Output
    # import sys
    # f = open('.\pyomomodel.txt', 'w')
    # standard = sys.stdout
    # sys.stdout = f
    # m.pprint()
    # sys.stdout = standard

    report = build_model_size_report(m)
    print("Num constraints: ", report.activated.constraints)
    print("Num variables: ", report.activated.variables)
    
    io_options = dict(
                add_options=['GAMS_MODEL.optfile = 1;','$onecho > baron.opt', 'reslim 180\n  NumLoc 20\n CompIIS 1', '$offecho'], 
                )

    # solver_options = {"reslim": 2}
    solver = pyo.SolverFactory('gams')
    results = solver.solve(m, solver='baron', keepfiles=True, tee=True, io_options=io_options)

    try:
        c_product_epox.append(pyo.value(m.component("c_out")["EPOX"]))
        c_educt_limo.append(pyo.value(m.component("c_out")["LIMO"]))
    except:
        c_product_epox.append(-1)
        c_educt_limo.append(-1)

    if Tcs[i] == 300:
        var_values = {}
        for v in m.component_objects(pyo.Var, active=True):
            var_object = getattr(m, str(v))
            for index in var_object:
                var_values[str(v) + str(index)] = var_object[index].value

sample = range(0,130)

c_educt_limo_out = []  
c_product_epox_out = []  
Tcs_out = []
for i in sample:
    Tcs_out.append(Tcs[i])
    c_educt_limo_out.append(c_educt_limo[i])
    c_product_epox_out.append(c_product_epox[i])

plt.plot(Tcs_out, c_product_epox_out, label="Epoxide")
plt.plot(Tcs_out, c_educt_limo_out, label="Limonene")
plt.xlabel("Temperature / [K]")
plt.ylabel("Concentration / [kmol/m3]")
plt.legend()
plt.show()


print()