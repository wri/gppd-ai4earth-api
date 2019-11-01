""" This file contains functions to estimate generation, capacity factor, and other 
formulas related to the dataset.
"""

def generation():
    
    pass

def capacity_factor(generation_ghw, capacity_mw, num_days):
    """ Computes the capacity factor given the parameters
    Formula: capacity_factor = (generation_ghw) / (num_days * num_hours * capacity_mw)

    Parameters
    generation_gwh: float, the generation in gigawatt-hours of the power plant
    capacity_mw: float, the maximum capacity in megawatts of the power plant
    num_days: int, the number of days it took to produce genneration_mhw amount of energy

    Return
    float
    """
    # 24 is number of hours in a day, 1000 is the conversion factor
    capacity_factor = generation_gwh / ((capacity_mw * 24 * num_days) /1000)
    assert 0 <= capacity_factor <= 1, "Computation Error: capacity_facotr outside of range [0,1]"

    return capacity_factor
