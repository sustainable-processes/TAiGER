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

    m.c_out_aq = pyo.Var(m.i, bounds=(0,100))
    m.c_out_org = pyo.Var(m.i, bounds=(0,100))
    m.c_in_aq = pyo.Param(m.i, initialize={"CAT":0,"H2O2":9.87,"ACAT":0,"H2O":42.68,"LIMO":0,"EPOX":0})
    m.c_in_org = pyo.Param(m.i, initialize={"CAT":0.0617,"H2O2":0,"ACAT":0,"H2O":0,"LIMO":8.16,"EPOX":0})
    m.V_dot_aq = pyo.Param(initialize=V_dot_aqs[i])
    m.V_dot_org = pyo.Param(initialize=V_dot_orgs[i])
    m.V_aq = pyo.Var(bounds=(0,1))
    m.V_org = pyo.Var(bounds=(0,1))
    m.J = pyo.Var(m.i, bounds=(-10,10))

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

    m.kL_aq = pyo.Var(m.i, bounds=(0,10))
    m.kL_aq["LIMO"].fix(0)
    m.kL_aq["H2O2"].fix(0)
    m.kL_aq["EPOX"].fix(0)
    m.kL_org = pyo.Var(m.i, bounds=(0,10))
    m.kL_org["LIMO"].fix(0)
    m.kL_org["H2O2"].fix(0)
    m.kL_org["EPOX"].fix(0)

    m.eps = pyo.Param(initialize=1e-22)

    m.A = pyo.Var(bounds=(0,1000000))
    m.a = pyo.Var(bounds=(0,10000000))

    m.K_mt = pyo.Var(m.i, bounds=(0,10))

    m.H = pyo.Param(m.i, initialize={"CAT":0.1,"H2O2":1,"ACAT":0.1,"H2O":-99,"LIMO":0,"EPOX":0})
    m.H_water = pyo.Var(bounds=(0,0.1))

    m.Tc = pyo.Param(initialize=Tcs[i]) # K

    m.vis_aq = pyo.Var(bounds=(1e-9,0.1))
    m.vis_org = pyo.Var(bounds=(1e-9,0.1))

    m.MV_p = pyo.Param(initialize=584.4) # cm3/mol
    m.MV_org = pyo.Param(initialize=189) # cm3/mol

    m.Pp = pyo.Param(initialize=1141)
    m.Pl = pyo.Param(initialize=357.9)
    m.Pv = pyo.Var(bounds=(0,10000)) # W/m3

    m.D_aq = pyo.Var(bounds=(1e-9,1))
    m.D_org = pyo.Var(bounds=(1e-9,1))

    m.rho_aq = pyo.Var(bounds=(1e-9,1100))
    m.rho_org = pyo.Var(bounds=(1e-9,1500))

    m.d = pyo.Param(initialize=0.17) # m
    m.N = pyo.Param(initialize=1000) # RPM

    m.dp = pyo.Param(initialize=1e-5) # m

    m.l_aq = pyo.Var(bounds=(-3,3))

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

    def _balance_aq(m, i):
        return (0 == (m.c_in_aq[i] - m.c_out_aq[i]) * m.V_dot_aq + m.V_aq * m.r_aq_i[i] - m.A * m.J[i])
    m.balance_aq = pyo.Constraint(m.i, rule=_balance_aq)

    def _balance_org(m, i):
        return (0 == (m.c_in_org[i] - m.c_out_org[i]) * m.V_dot_org + m.V_org * m.r_org_i[i] + m.A * m.J[i])
    m.balance_org = pyo.Constraint(m.i, rule=_balance_org)
    
    def _mt_flux(m,i):
        if i in ["H2O"]:
            return m.J[i] == m.K_mt[i] * (m.c_out_aq[i] - m.H_water*m.c_out_org[i])
        else:
            return m.J[i] == m.K_mt[i] * (m.c_out_aq[i] - m.H[i]*m.c_out_org[i])
    m.mt_flux = pyo.Constraint(m.i, rule=_mt_flux)

    def _overall_mt(m,i):
        if i in ["CAT","ACAT"]:
            return m.K_mt[i] == 1/(m.H[i]/(m.kL_org[i]+m.eps) + 1/(m.kL_aq[i]+m.eps))
        elif i in ["H2O"]:
            return m.K_mt[i] == 1/(m.H_water/(m.kL_org[i]+m.eps) + 1/(m.kL_aq[i]+m.eps))
        else:
            return m.K_mt[i] == 0
    m.overall_mt = pyo.Constraint(m.i, rule=_overall_mt)

    def _ratelaw_aq(m):
        return m.r_aq == m.k_aq * m.c_out_aq["CAT"] * m.c_out_aq["H2O2"]
    m.ratelaw_aq = pyo.Constraint(rule=_ratelaw_aq)

    def _ratelaw_org(m):
        return m.r_org == m.k_org * m.c_out_org["ACAT"] * m.c_out_org["LIMO"]
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

    def _diff_PTC_to_limo(m):
        return m.D_org == 1.55e-8 * (m.Tc**1.29) * ((m.Pl**0.5)/(m.Pp**0.42)) / ((m.vis_org+m.eps)**0.92) / (m.MV_org**0.23) 
    m.diff_PTC_to_limo = pyo.Constraint(rule=_diff_PTC_to_limo)

    def _viscosity_org(m):
        return m.vis_org == 0.0286 * pyo.exp(-0.012 * m.Tc)
    m.viscosity_org = pyo.Constraint(rule=_viscosity_org)

    def _diff_PTC_to_h2o(m):
        return m.D_aq == 1.25e-8 * (m.MV_p**(-0.19) - 0.292) * (m.Tc**1.52) * ((m.vis_aq+m.eps)**(m.l_aq)) 
    m.diff_PTC_to_h2o = pyo.Constraint(rule=_diff_PTC_to_h2o)

    def _viscosity_aq(m):
        return m.vis_aq == 0.2953 * pyo.exp(-0.019 * m.Tc)
    m.viscosity_aq = pyo.Constraint(rule=_viscosity_aq)
    
    def _diff_exponent_aq(m):
        return m.l_aq == (0.958/m.MV_p) - 1.12
    m.diff_exponent_aq = pyo.Constraint(rule=_diff_exponent_aq)

    def _mt_coefficient_org(m):
        return m.kL_org["ACAT"] == 0.13 * ((m.Pv * m.vis_org / ((m.rho_org+m.eps)**2))**(1/4)) * ((m.D_org * m.rho_org / (m.vis_org+m.eps))**(2/3))
    m.mt_coefficient_org = pyo.Constraint(rule=_mt_coefficient_org)

    def _mt_coefficient_aq(m):
        return m.kL_aq["ACAT"] == 0.13 * ((m.Pv * m.vis_aq / ((m.rho_aq+m.eps)**2))**(1/4)) * ((m.D_aq * m.rho_aq / (m.vis_aq+m.eps))**(2/3))
    m.mt_coefficient_aq = pyo.Constraint(rule=_mt_coefficient_aq)

    def _mt_coefficient_rest1_org(m):
        return (m.kL_org["ACAT"] == m.kL_org["CAT"]) 
    m.mt_coefficient_rest1_org = pyo.Constraint(rule=_mt_coefficient_rest1_org)

    def _mt_coefficient_rest2_org(m):
        return (m.kL_org["ACAT"] == m.kL_org["H2O"])
    m.mt_coefficient_rest2_org = pyo.Constraint(rule=_mt_coefficient_rest2_org)

    def _mt_coefficient_rest1_aq(m):
        return (m.kL_aq["ACAT"] == m.kL_aq["CAT"])
    m.mt_coefficient_rest1_aq = pyo.Constraint(rule=_mt_coefficient_rest1_aq)

    def _mt_coefficient_rest2_aq(m):
        return (m.kL_aq["ACAT"] == m.kL_aq["H2O"])
    m.mt_coefficient_rest2_aq = pyo.Constraint(rule=_mt_coefficient_rest2_aq)

    def _stirrer_power(m):
        return m.Pv == (0.2 * ((1-m.phi) * m.rho_aq + m.phi * m.rho_org) * ((m.N/60)**3) * (m.d**5)) / (m.V_total+m.eps)
    m.stirrer_power = pyo.Constraint(rule=_stirrer_power)
    
    def _density_aq(m):
        return m.rho_aq == (-0.0039 * m.Tc**2) + (2.0516 * m.Tc) + 727.52
    m.density_aq = pyo.Constraint(rule=_density_aq)

    def _density_org(m):
        return m.rho_org == (-0.7889 * m.Tc) + 1075.8
    m.density_org = pyo.Constraint(rule=_density_org)

    def _interfacial_area(m):
        return m.a == 6 * m.phi / m.dp
    m.interfacial_area = pyo.Constraint(rule=_interfacial_area)

    def _complete_area(m):
        return m.A == m.a * m.V_total
    m.complete_area = pyo.Constraint(rule=_complete_area)

    def _henry_h2o(m):
        return m.H_water == (2.11e-7*m.Tc**2) - (1.12e-4*m.Tc)+1.55e-2
    m.henry_h20 = pyo.Constraint(rule=_henry_h2o)

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

    # report = build_model_size_report(m)
    # print("Num constraints: ", report.activated.constraints)
    # print("Num variables: ", report.activated.variables)
    
    io_options = dict(
                add_options=['GAMS_MODEL.optfile = 1;','$onecho > baron.opt', 'reslim 180\n  NumLoc 20\n CompIIS 1', '$offecho'], 
                )

    # solver_options = {"reslim": 2}
    solver = pyo.SolverFactory('gams')
    results = solver.solve(m, solver='baron', keepfiles=True, tee=True, io_options=io_options)

    try:
        c_product_epox.append(pyo.value(m.component("c_out_org")["EPOX"]))
        c_educt_limo.append(pyo.value(m.component("c_out_org")["LIMO"]))
        kL_aq.append(pyo.value(m.component("kL_aq")["ACAT"]))
        kL_org.append(pyo.value(m.component("kL_org")["ACAT"]))
    except:
        c_product_epox.append(-1)
        c_educt_limo.append(-1)
        kL_aq.append(-1)
        kL_org.append(-1)

    if Tcs[i] == 347:
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