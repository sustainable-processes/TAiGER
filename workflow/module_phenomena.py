from module_compartmentalization import *
from classes_state_representation import *

class PhenomenaModule:

    def get_phenomena(self,case_study,modus):

        # For every desired case study, set up the constitutive equations for the phenomena
        ## Here: Case Study 1: In silico Phase Transfer Catalysis
        if case_study == "insilico-ptc":
            
            # A phenomenon object is a collection of constitutive equations
            phase1 = Phenomenon(identifier="phase1", type="phase", can_compartment=True, can_interface=False)
            phase2 = Phenomenon(identifier="phase2", type="phase", can_compartment=True, can_interface=False)

            convection = Phenomenon(identifier="convection", type="convection", can_compartment=False, can_interface=True)
            film_masstransfer = Phenomenon(identifier="film_masstransfer", type="diffusion", can_compartment=False, can_interface=True)

            # Every phenomenon gets a function that specifies the equations in terms of its host building block
            ## Equations are constructed in post-fix notation with the same state objects as Heyer 2023
            ### Here: CSTR gets mass transfer, viscosity, reaction equations etc.
            def phase1_state_lib(host):

                if type(host) == CSTR:

                    ## Internal masstransfer coefficient

                    # Check if certain symbols have been defined before (e.g. in the building block itself)
                    if not hasattr(host,'kL'):
                        host.kL = SymbTerminalNode(host.name + "_kL", "m." + host.name + "_kL[i,n]", ['i','n'], None, None, lb=1e-20, ub=10)

                    if not hasattr(host,'vis'):
                        host.vis = SymbTerminalNode(host.name + "_vis", "m." + host.name + "_vis[n]", ['n'], None, None, lb=1e-20, ub=0.1)
                    if not hasattr(host,'D'):
                        host.D = SymbTerminalNode(host.name + "_D", "m." + host.name + "_D[n]", ['n'], None, None, lb=1e-20, ub=1)
                    if not hasattr(host,'rho'):
                        host.rho = SymbTerminalNode(host.name + "_rho", "m." + host.name + "_rho[n]", ['n'], None, None, lb=0.1, ub=1500)

                    if not hasattr(host,'kL_discr'):
                        host.kL_discr = SymbTerminalNode(host.name + "_kL_discr", "m." + host.name + "_kL_discr[i,n]", ['i','n'], None, None, lb=0, ub=1)

                    # Construct equations and add them to library, if certain conditions are met
                    if any([interface.type == "diffusion" for interface in host.interfaces_in + host.interfaces_out]):
                        host.eq_library |= {
                            host.name + '_mt_coeff_aq': [host.kL,host.kL_discr,NumTerminalNode('0.13','0.13'),host.Pv,host.vis,host.math.multi,host.rho,host.rho,host.math.multi,host.math.divid,NumTerminalNode('0.25','0.25'),host.math.power,host.D,host.rho,host.math.multi,host.vis,host.math.divid,NumTerminalNode('(2/3)','(2/3)'),host.math.power,host.math.multi,host.math.multi,host.math.multi,host.math.equal_i], 
                        }

                    ## Internal diffusion coefficient
                    if not hasattr(host,'D'):
                        host.D = SymbTerminalNode(host.name + "_D", "m." + host.name + "_D[n]", ['n'], None, None, lb=1e-20, ub=1)
                    
                    host.lD = SymbTerminalNode(host.name + "_lD", "m." + host.name + "_lD[n]", ['n'], None, None, lb=-3, ub=3)
                    
                    host.MVp = SymbTerminalNode(host.name + "_MVp", "m." + host.name + "_MVp[n]", ['n'], None, None)
                    host.MV = SymbTerminalNode(host.name + "_MV", "m." + host.name + "_MV[n]", ['n'], None, None)
                    host.Pp = SymbTerminalNode(host.name + "_Pp", "m." + host.name + "_Pp[n]", ['n'], None, None)
                    host.Pl = SymbTerminalNode(host.name + "_Pl", "m." + host.name + "_Pl[n]", ['n'], None, None)

                    if not hasattr(host,'vis'):
                        host.vis = SymbTerminalNode(host.name + "_vis", "m." + host.name + "_vis[n]", ['n'], None, None, lb=1e-20, ub=0.1)

                    host.eq_library |= {
                        host.name + '_diff_aq': [host.D,NumTerminalNode('0.0000000125','0.0000000125'),host.MVp,NumTerminalNode('(-0.19)','(-0.19)'),host.math.power,NumTerminalNode('0.292','0.292'),host.math.minus,host.Tc,NumTerminalNode('1.52','1.52'),host.math.power,host.vis,host.lD,host.math.power,host.math.multi,host.math.multi,host.math.multi,host.math.equal],
                        host.name + '_diff_expo': [host.lD,NumTerminalNode('0.958','0.958'),host.MVp,host.math.divid,NumTerminalNode('1.12','1.12'),host.math.minus,host.math.equal]
                    }

                    ## Viscosity
                    if not hasattr(host,'vis'):
                        host.vis = SymbTerminalNode(host.name + "_vis", "m." + host.name + "_vis[n]", ['n'], None, None, lb=1e-20, ub=0.1)

                    host.eq_library |= {
                        host.name + '_vis_aq': [host.vis,NumTerminalNode('0.2953','0.2953'),NumTerminalNode('(-0.019)','(-0.019)'),host.Tc,host.math.multi,host.math.expon,host.math.multi,host.math.equal],
                    }

                    ## Density
                    if not hasattr(host,'rho'):
                        host.rho = SymbTerminalNode(host.name + "_rho", "m." + host.name + "_rho[n]", ['n'], None, None, lb=0.1, ub=1500)

                    host.eq_library |= {
                        host.name + '_rho_aq': [host.rho,NumTerminalNode('-0.0039','-0.0039'),host.Tc,NumTerminalNode('2','2'),host.math.power,host.math.multi,NumTerminalNode('2.0516','2.0516'),host.Tc,host.math.multi,NumTerminalNode('727.52','727.52'),host.math.plus,host.math.plus,host.math.equal],
                    }

                    # We can define some alternative equations that are exclusive to one another. For example, it makes no sense to include the viscosity correlation for the both the organic and aqeuous phase in the same compartment.
                    host.exclusive_eqs = [[host.name + '_diff_org',host.name + '_diff_aq'],[host.name + '_vis_org',host.name + '_vis_aq'],[host.name + '_rho_org',host.name + '_rho_aq']]

                    if not hasattr(host,'k_aq'):
                        host.k_aq = SymbTerminalNode(host.name + "_k_aq", "m." + host.name + "_k_aq[p,n]", ['p','n'], None, None, lb=0, ub=20)
                    if not hasattr(host,'r_aq'):
                        host.r_aq = SymbTerminalNode(host.name + "_r_aq", "m." + host.name + "_r_aq[p,n]", ['p','n'], None, None, lb=0, ub=1)
                    
                    host.nu_ip_aq = SymbTerminalNode(host.name + "_nu_ip_aq", "m." + host.name + "_nu_ip_aq[i,p]", ['i','p'], None, None)
                    host.ord_ip_aq = SymbTerminalNode(host.name + "_ord_ip_aq", "m." + host.name + "_ord_ip_aq[i,p]", ['i','p'], None, None)
                    host.k0_aq = SymbTerminalNode(host.name + "_k0_aq", "m." + host.name + "_k0_aq[p,n]", ['p','n'], None, None)
                    host.E_aq = SymbTerminalNode(host.name + "_E_aq", "m." + host.name + "_E_aq[p,n]", ['p','n'], None, None)
                    host.Tref_aq = SymbTerminalNode(host.name + "_Tref_aq", "m." + host.name + "_Tref_aq[p,n]", ['p','n'], None, None)
                    host.Rg_aq = NumTerminalNode('8.314','8.314')
                    
                    host.eq_library |= {
                        host.name + '_stoich_aq': [NumTerminalNode('0','0'), host.r_aq, host.nu_ip_aq, host.math.multi, host.math.sumop_p, getattr(host, "phase1R"), host.math.minus, host.math.equal_ip],
                        host.name + '_ratelaw_aq': [NumTerminalNode('0','0'), host.k_aq, host.F_out, host.V_dot, host.math.divid, host.ord_ip_aq, host.math.power, host.math.prodop_i, host.math.multi, host.r_aq, host.math.minus, host.math.equal_p], 
                        host.name + '_arrhenius_aq': [host.k_aq,host.k0_aq,NumTerminalNode('0','0'),host.E_aq,host.math.minus,host.Rg_aq,host.math.divid,NumTerminalNode('1','1'),host.Tc,host.math.divid,NumTerminalNode('1','1'),host.Tref_aq,host.math.divid,host.math.minus,host.math.multi,host.math.expon,host.math.multi,host.math.equal_p]
                    }

            def phase2_state_lib(host):
                
                if type(host) == CSTR:

                    ## Internal masstransfer coefficient
                    if not hasattr(host,'kL'):
                        host.kL = SymbTerminalNode(host.name + "_kL", "m." + host.name + "_kL[i,n]", ['i','n'], None, None, lb=1e-20, ub=10)

                    if not hasattr(host,'vis'):
                        host.vis = SymbTerminalNode(host.name + "_vis", "m." + host.name + "_vis[n]", ['n'], None, None, lb=1e-20, ub=0.1)
                    if not hasattr(host,'D'):
                        host.D = SymbTerminalNode(host.name + "_D", "m." + host.name + "_D[n]", ['n'], None, None, lb=1e-20, ub=1)
                    if not hasattr(host,'rho'):
                        host.rho = SymbTerminalNode(host.name + "_rho", "m." + host.name + "_rho[n]", ['n'], None, None, lb=0.1, ub=1500)

                    if not hasattr(host,'kL_discr'):
                        host.kL_discr = SymbTerminalNode(host.name + "_kL_discr", "m." + host.name + "_kL_discr[i,n]", ['i','n'], None, None, lb=0, ub=1)

                    if any([interface.type == "diffusion" for interface in host.interfaces_in + host.interfaces_out]):
                        host.eq_library |= {
                            host.name + '_mt_coeff_org': [host.kL,host.kL_discr,NumTerminalNode('0.13','0.13'),host.Pv,host.vis,host.math.multi,host.rho,host.rho,host.math.multi,host.math.divid,NumTerminalNode('0.25','0.25'),host.math.power,host.D,host.rho,host.math.multi,host.vis,host.math.divid,NumTerminalNode('(2/3)','(2/3)'),host.math.power,host.math.multi,host.math.multi,host.math.multi,host.math.equal_i], 
                    }

                    ## Internal diffusion coefficient
                    if not hasattr(host,'D'):
                        host.D = SymbTerminalNode(host.name + "_D", "m." + host.name + "_D[n]", ['n'], None, None, lb=1e-20, ub=1)
                    
                    host.lD = SymbTerminalNode(host.name + "_lD", "m." + host.name + "_lD[n]", ['n'], None, None, lb=-3, ub=3)
                    
                    host.MVp = SymbTerminalNode(host.name + "_MVp", "m." + host.name + "_MVp[n]", ['n'], None, None)
                    host.MV = SymbTerminalNode(host.name + "_MV", "m." + host.name + "_MV[n]", ['n'], None, None)
                    host.Pp = SymbTerminalNode(host.name + "_Pp", "m." + host.name + "_Pp[n]", ['n'], None, None)
                    host.Pl = SymbTerminalNode(host.name + "_Pl", "m." + host.name + "_Pl[n]", ['n'], None, None)

                    if not hasattr(host,'vis'):
                        host.vis = SymbTerminalNode(host.name + "_vis", "m." + host.name + "_vis[n]", ['n'], None, None, lb=1e-20, ub=0.1)

                    host.eq_library |= {
                        host.name + '_diff_org': [host.D,NumTerminalNode('0.0000000155','0.0000000155'),host.Tc,NumTerminalNode('1.29','1.29'),host.math.power,host.Pl,NumTerminalNode('0.5','0.5'),host.math.power,host.Pp,NumTerminalNode('(-0.42)','(-0.42)'),host.math.power,host.vis,NumTerminalNode('-0.92','-0.92'),host.math.power,host.MV,NumTerminalNode('(-0.23)','(-0.23)'),host.math.power,host.math.multi,host.math.multi,host.math.multi,host.math.multi,host.math.multi,host.math.equal], 
                    }

                    ## Viscosity
                    if not hasattr(host,'vis'):
                        host.vis = SymbTerminalNode(host.name + "_vis", "m." + host.name + "_vis[n]", ['n'], None, None, lb=1e-20, ub=0.1)

                    host.eq_library |= {
                        host.name + '_vis_org': [host.vis,NumTerminalNode('0.0286','0.0286'),NumTerminalNode('(-0.012)','(-0.012)'),host.Tc,host.math.multi,host.math.expon,host.math.multi,host.math.equal],
                    }

                    ## Density
                    if not hasattr(host,'rho'):
                        host.rho = SymbTerminalNode(host.name + "_rho", "m." + host.name + "_rho[n]", ['n'], None, None, lb=0.1, ub=1500)

                    host.eq_library |= {
                        host.name + '_rho_org': [host.rho,NumTerminalNode('-0.7889','-0.7889'),host.Tc,host.math.multi,NumTerminalNode('1075.8','1075.8'),host.math.plus,host.math.equal],
                    }

                    host.exclusive_eqs = [[host.name + '_diff_org',host.name + '_diff_aq'],[host.name + '_vis_org',host.name + '_vis_aq'],[host.name + '_rho_org',host.name + '_rho_aq']]

                    if not hasattr(host,'k_org'):
                        host.k_org = SymbTerminalNode(host.name + "_k_org", "m." + host.name + "_k_org[p,n]", ['p','n'], None, None, lb=0, ub=20)
                    if not hasattr(host,'r_org'):
                        host.r_org = SymbTerminalNode(host.name + "_r_org", "m." + host.name + "_r_org[p,n]", ['p','n'], None, None, lb=0, ub=1)
                    
                    host.nu_ip_org = SymbTerminalNode(host.name + "_nu_ip_org", "m." + host.name + "_nu_ip_org[i,p]", ['i','p'], None, None)
                    host.ord_ip_org = SymbTerminalNode(host.name + "_ord_ip_org", "m." + host.name + "_ord_ip_org[i,p]", ['i','p'], None, None)
                    host.k0_org = SymbTerminalNode(host.name + "_k0_org", "m." + host.name + "_k0_org[p,n]", ['p','n'], None, None)
                    host.E_org = SymbTerminalNode(host.name + "_E_org", "m." + host.name + "_E_org[p,n]", ['p','n'], None, None)
                    host.Tref_org = SymbTerminalNode(host.name + "_Tref_org", "m." + host.name + "_Tref_org[p,n]", ['p','n'], None, None)
                    host.Rg_org = NumTerminalNode('8.314','8.314')
                    
                    host.eq_library |= {
                        host.name + '_stoich_org': [NumTerminalNode('0','0'), host.r_org, host.nu_ip_org, host.math.multi, host.math.sumop_p, getattr(host, "phase2R"), host.math.minus, host.math.equal_ip],
                        host.name + '_ratelaw_org': [NumTerminalNode('0','0'), host.k_org, host.F_out, host.V_dot, host.math.divid, host.ord_ip_org, host.math.power, host.math.prodop_i, host.math.multi, host.r_org, host.math.minus, host.math.equal_p], 
                        host.name + '_arrhenius_org': [host.k_org,host.k0_org,NumTerminalNode('0','0'),host.E_org,host.math.minus,host.Rg_org,host.math.divid,NumTerminalNode('1','1'),host.Tc,host.math.divid,NumTerminalNode('1','1'),host.Tref_org,host.math.divid,host.math.minus,host.math.multi,host.math.expon,host.math.multi,host.math.equal_p]
                    }

            # Give function to phenomenon objects
            phase1.generate_eqlib = phase1_state_lib
            phase2.generate_eqlib = phase2_state_lib

            def film_masstransfer_lib(host):
                if not hasattr(host,'KL'):  
                    host.KL = SymbTerminalNode(host.name + "_KL", "m." + host.name + "_KL[i,n]", ['i','n'], None, None, lb=1e-20, ub=10)
                if not hasattr(host,'a'):
                    host.a = SymbTerminalNode(host.name + "_a", "m." + host.name + "_a[n]", ['n'], None, None, lb=0, ub=10000000)
                if not hasattr(host.compartment_from,'A'):
                    host.A = SymbTerminalNode(host.name + "_A", "m." + host.name + "_A[n]", ['n'], None, None, lb=0, ub=1000000)
                if not hasattr(host,'Pv'):
                    host.Pv = SymbTerminalNode(host.name + "_Pv", "m." + host.name + "_Pv[n]", ['n'], None, None, lb=0.1, ub=10000)
                if not hasattr(host,'V_total'):
                    host.V_total = SymbTerminalNode(host.name + "_V_total", "m." + host.name + "_V_total[n]", ['n'], None, None, lb=1e-3, ub=1)
                if not hasattr(host,'phi'):
                    host.phi = SymbTerminalNode(host.name + "_phi", "m." + host.name + "_phi[n]", ['n'], None, None, lb=0, ub=1)

                if not hasattr(host,'H'):
                    host.H = SymbTerminalNode(host.name + "_H", "m." + host.name + "_H[i,n]", ['i','n'], None, None)
                if not hasattr(host.compartment_from,'kL'):
                    host.compartment_from.kL = SymbTerminalNode(host.compartment_from.name + "_kL", "m." + host.compartment_from.name + "_kL[i,n]", ['i','n'], None, None, lb=1e-20, ub=10)
                if not hasattr(host.compartment_to,'kL'):
                    host.compartment_to.kL = SymbTerminalNode(host.compartment_to.name + "_kL", "m." + host.compartment_to.name + "_kL[i,n]", ['i','n'], None, None, lb=1e-20, ub=10)

                if not hasattr(host.compartment_from,'rho'):
                    host.compartment_from.rho = SymbTerminalNode(host.name + "_rho", "m." + host.name + "_rho[n]", ['n'], None, None, lb=0.1, ub=1500)
                if not hasattr(host.compartment_to,'rho'):
                    host.compartment_to.rho = SymbTerminalNode(host.name + "_rho", "m." + host.name + "_rho[n]", ['n'], None, None, lb=0.1, ub=1500)

                host.dp = SymbTerminalNode(host.name + "_dp", "m." + host.name + "_dp[n]", ['n'], None, None)
                host.d = SymbTerminalNode(host.name + "_d", "m." + host.name + "_d[n]", ['n'], None, None)
                host.N = SymbTerminalNode(host.name + "_N", "m." + host.name + "_N[n]", ['n'], None, None)

                if not hasattr(host,'kL_discr'):
                    host.kL_discr = SymbTerminalNode(host.name + "_kL_discr", "m." + host.name + "_kL_discr[i,n]", ['i','n'], None, None, lb=0, ub=1)

                host.eq_library |= {
                    host.name + '_mt_flux': [host.J_diff, host.KL, host.compartment_from.F_out, host.compartment_from.V_dot, host.math.divid, host.H, host.compartment_to.F_out, host.compartment_to.V_dot, host.math.divid, host.math.multi, host.math.minus, host.math.multi, host.math.equal_i],
                    host.name + '_overall_mt_coeff': [host.KL,host.kL_discr,NumTerminalNode('1','1'),host.H,host.compartment_to.kL,NumTerminalNode('1e-22','1e-22'),host.math.plus,host.math.divid,NumTerminalNode('1','1'),host.compartment_from.kL,NumTerminalNode('1e-22','1e-22'),host.math.plus,host.math.divid,host.math.plus,host.math.divid,host.math.multi,host.math.equal_i], 
                    host.name + '_specific_area': [host.a,NumTerminalNode('6','6'),host.phi,host.dp,host.math.divid,host.math.multi,host.math.equal],
                    host.name + '_total_area': [host.A,host.a,host.compartment_from.V,host.compartment_to.V,host.math.plus,host.math.multi,host.math.equal],                
                    host.name + '_power': [host.Pv,NumTerminalNode('0.2','0.2'),NumTerminalNode('1','1'),host.phi,host.math.minus,host.compartment_from.rho,host.math.multi,host.phi,host.compartment_to.rho,host.math.multi,host.math.plus,host.N,NumTerminalNode('60','60'),host.math.divid,NumTerminalNode('3','3'),host.math.power,host.d,NumTerminalNode('5','5'),host.math.power,host.math.multi,host.math.multi,host.math.multi,host.compartment_from.V,host.compartment_to.V,host.math.plus,NumTerminalNode('1e-5','1e-5'),host.math.multi,host.math.divid,host.math.equal],
                    host.name + '_phase_ratio_from': [host.phi,host.compartment_from.V,host.compartment_from.V,host.compartment_to.V,host.math.plus,host.math.divid,host.math.equal],
                    host.name + '_phase_ratio_to': [NumTerminalNode('1','1'),host.phi,host.math.minus,host.compartment_to.V,host.compartment_from.V,host.compartment_to.V,host.math.plus,host.math.divid,host.math.equal],
                    host.name + '_phase_flow_ratio': [host.phi,host.compartment_from.V_dot,host.compartment_from.V_dot,host.compartment_to.V_dot,host.math.plus,host.math.divid,host.math.equal],                
                }

            film_masstransfer.generate_eqlib = film_masstransfer_lib

            # Put all phenomena is a list that is then given to the following workflow steps
            phenomena_list = [phase1, phase2, convection, film_masstransfer]

            return phenomena_list
            
        if case_study == "tcr-rtd":

            if modus == "rtd":

                # The regular RTD case study needs no phenomena as only the hydrodynamics are considered that are completely specified by the building blocks themselves
                phenomena_list = []

                return phenomena_list
            
            # To put in the reaction data into the hydrodynamic model afterwards, we create a phenomenon for the esterification reaction from Heyer 2023
            if modus == "hierarchic_data":
                
                ap_reaction = Phenomenon(identifier="ap_reaction", type="reaction", can_compartment=True, can_interface=False)

                ap_reaction.nu_i = SymbTerminalNode(ap_reaction.identifier + "_nu_i", "m." + ap_reaction.identifier + "_nu_i[i]", ['i'], None, None)
                ap_reaction.k = SymbTerminalNode(ap_reaction.identifier + "_k", "m." + ap_reaction.identifier + "_k", None, None, None, special_type="parameter", lb=0, ub=0.1)
                ap_reaction.ord_i = SymbTerminalNode(ap_reaction.identifier + "_ord_i", "m." + ap_reaction.identifier + "_ord_i[i]", ['i'], None, None)
                ap_reaction.k0 = SymbTerminalNode(ap_reaction.identifier + "_k0", "m." + ap_reaction.identifier + "_k0", None, None, None, special_type="parameter", lb=0, ub=0.1)
                ap_reaction.E = SymbTerminalNode(ap_reaction.identifier + "_E", "m." + ap_reaction.identifier + "_E", None, None, None, special_type="parameter")
                ap_reaction.Rg = SymbTerminalNode(ap_reaction.identifier + "_Rg", "m." + ap_reaction.identifier + "_Rg", None, None, None)
                ap_reaction.Tref = SymbTerminalNode(ap_reaction.identifier + "_Tref", "m." + ap_reaction.identifier + "_Tref", None, None, None, special_type="parameter", lb=280, ub=300)

                def reaction_lib(host):
                        
                    host.r = SymbTerminalNode(host.name + "_r", "m." + host.name + "_r", None, None, None)

                    host.eq_library |= {
                        host.name + '_stoich': [NumTerminalNode('0','0'), host.r, ap_reaction.nu_i, host.math.multi, host.ap_reactionR, host.math.minus, host.math.equal_isolo],
                        host.name + '_ratelaw': [NumTerminalNode('0','0'), ap_reaction.k, host.c_out, ap_reaction.ord_i, host.math.power, host.math.prodop_i, host.math.multi, host.r, host.math.minus, host.math.equal_noind], 
                        ap_reaction.identifier + '_arrhenius': [ap_reaction.k,ap_reaction.k0,NumTerminalNode('0','0'),ap_reaction.E,host.math.minus,ap_reaction.Rg,host.math.divid,NumTerminalNode('1','1'),host.T,host.math.divid,NumTerminalNode('1','1'),ap_reaction.Tref,host.math.divid,host.math.minus,host.math.multi,host.math.expon,host.math.multi,host.math.equal_noind]
                    }

                ap_reaction.generate_eqlib = reaction_lib

                phenomena_list = [ap_reaction]

                return phenomena_list
