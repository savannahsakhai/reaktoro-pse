from parameter_sweep import LinearSample, parameter_sweep, PredeterminedFixedSample
from pyomo.environ import (
    ConcreteModel,
    value,
    Constraint,
    Objective,
    Var,
    TransformationFactory,
    units as pyunits,
    check_optimal_termination,
    assert_optimal_termination,
)
from pyomo.environ import units as pyunits
import reaktoro_pse.prop_analysis.MVC_reaktoro as reaktoro_flowsheet
import time

def set_up_sensitivity_MVC(flowsheet):
    outputs = {}

    m = flowsheet.build()
    flowsheet.set_operating_conditions(m)
    flowsheet.add_Q_ext(m, time_point=m.fs.config.time)
    flowsheet.initialize_system(m)
    flowsheet.scale_costs(m)
    flowsheet.fix_outlet_pressures(m)
    flowsheet.activate_reaktoro(m)
    m.fs.objective = Objective(expr=m.fs.Q_ext[0])
    flowsheet.solve(m)

    # set up the model for optimization
    flowsheet.set_up_optimization(m)

    opt_function = flowsheet.solve

    # create outputs
    outputs["LCOW"] = m.fs.costing.LCOW
    outputs["SEC"] = m.fs.costing.specific_energy_consumption
    outputs["Evaporator area"] = m.fs.evaporator.area
    outputs["Compressor pressure ratio"] = m.fs.compressor.pressure_ratio
    outputs["Brine HX area"] = m.fs.hx_brine.area
    outputs["Dist HX area"] = m.fs.hx_distillate.area
        
    return outputs, opt_function, m


def run_analysis_MVC(case_num=1, flowsheet=reaktoro_flowsheet, interpolate_nan_outputs=True, output_filename=None):
    
    if output_filename is None:
        output_filename = "sensitivity_" + str(case_num) + ".csv"

    outputs, opt_function, m = set_up_sensitivity_MVC(flowsheet)

    sweep_params = {}

    if case_num == 1:
        # sensitivity analysis
        sweep_params = dict()
        sweep_params["Water Recovery"] = LinearSample(m.fs.recovery[0], 0.5, 0.7, 11)

    elif case_num == 2:
        # sensitivity analysis
        sweep_params = dict()
        sweep_params["Inlet Salinity"] = PredeterminedFixedSample(
            m.fs.feed.properties[0].mass_frac_phase_comp["Liq", "TDS"], [.070, .100, .125, .150]
        )
        sweep_params["Water Recovery"] = LinearSample(m.fs.recovery[0], 0.4, 0.8, 5)
    elif case_num == 3:
        # sensitivity analysis
        sweep_params = dict()
        sweep_params["Inlet Salinity"] = LinearSample(
            m.fs.feed.properties[0].mass_frac_phase_comp["Liq", "TDS"], .070,.150, 17
        )

    else:
        raise ValueError(f"{case_num} is not yet implemented")


    global_results = parameter_sweep(
        m,
        sweep_params,
        outputs,
        csv_results_file_name=output_filename,
        optimize_function=opt_function,
        interpolate_nan_outputs=interpolate_nan_outputs,
        # reinitialize_function=flowsheet.reinitialize_system,
        # reinitialize_before_sweep=True,
    )

    return global_results, sweep_params, m


if __name__ == "__main__":
    # start_time = time.time()
    # results, sweep_params, m = run_analysis_MVC(case_num=1, output_filename="data_MVC_reaktoro.csv")
    # end_time= time.time()
    # elapsed_time_1 = end_time - start_time

    start_time = time.time()
    results, sweep_params, m = run_analysis_MVC(case_num=3, output_filename="data_MVC_reaktoro_1D.csv")
    end_time= time.time()
    elapsed_time_2 = end_time - start_time

    # print(elapsed_time_1)
    print(elapsed_time_2)