from parameter_sweep import LinearSample, parameter_sweep, PredeterminedFixedSample
from pyomo.environ import units as pyunits
import reaktoroblock_flowsheet_bw as reaktoro_flowsheet

def set_up_sensitivity():
    outputs = {}

    

    m, water_composition = reaktoro_flowsheet.build()
    reaktoro_flowsheet.initialize_system(m, water_composition)
    reaktoro_flowsheet.solve(m)


    # optimize_kwargs = {"fail_flag": False}
    opt_function = reaktoro_flowsheet.solve

    # create outputs
    # outputs["TDS mg/L"] = m.fs.bw.TDS
    outputs["Density"] = m.fs.bw.density
    # outputs["Osmotic Pressure"] = m.fs.bw.osmotic_pressure
    outputs["Enthalpy"] = m.fs.bw.enthalpy
    outputs["Vapor Pressure"] = m.fs.bw.vapor_pressure
   
    return outputs, opt_function, m


def run_analysis(case_num=4, nx=2, interpolate_nan_outputs=True, output_filename=None):

    if output_filename is None:
        output_filename = "sensitivity_full_flowsheet_" + str(case_num) + ".csv"

    outputs, opt_function, m = set_up_sensitivity()

    sweep_params = {}

    if case_num == 1:
        sweep_params = dict()
        sweep_params["Feed Mass Frac"] = PredeterminedFixedSample(
           m.fs.feed[0].mass_frac_phase_comp["Liq", "NaCl"], [500/1e6, 1000/1e6, 5000/1e6, 10000/1e6]
        )
        sweep_params["Mono to Di Ratio"] = PredeterminedFixedSample(
            m.fs.bw.mono_di_ratio, [1/3, 1/2, 1, 2, 3]
        )
        sweep_params["Temperature"] = LinearSample(
            m.fs.bw.temperature, 25 + 273.15, 95 + 273.15, 8
        )
    else:
        raise ValueError(f"{case_num} is not yet implemented")

    global_results = parameter_sweep(
        m,
        sweep_params,
        outputs,
        csv_results_file_name=output_filename,
        optimize_function=opt_function,
        # optimize_kwargs=optimize_kwargs,
        interpolate_nan_outputs=interpolate_nan_outputs,
    )

    return global_results, sweep_params, m


if __name__ == "__main__":
    results, sweep_params, m = run_analysis(case_num=1, output_filename="data_property_bw_reaktoro.csv")
    # print(results)
