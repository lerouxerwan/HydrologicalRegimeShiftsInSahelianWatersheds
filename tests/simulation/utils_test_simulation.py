def check_simulation_data(simulation, final_years: list[int]):
    assert len(simulation.years) > 0
    actual_final_year = simulation.years[-1]
    assert actual_final_year in final_years, f'{actual_final_year} != {final_years}'
