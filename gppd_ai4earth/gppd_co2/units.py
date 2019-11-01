def standard_unit(type='quantity'):
    if type not in ('quantity', 'rate'):
        raise ValueError("must by one of {'quantity', 'rate'}")
    return {'quantity': 'Kg', 'rate': 'Kg/KWh'}.get(type)

