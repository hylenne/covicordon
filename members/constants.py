from members.models import Config

# VALOR_UR = 1621
# VALOR_GC = 3500
# COSTO_CUARTO_UR = 2.965 # UNIDADES REAJUSTABLES
# FONDO_MANTENIMIENTO = 0.42 # UNIDADES REAJUSTABLES


def gen_cuota_social(socio):
    global_config = Config.get_config()
    VALOR_UR = global_config.ur
    VALOR_GC = global_config.gc
    COSTO_CUARTO_UR = global_config.bedroom_prices  # UNIDADES REAJUSTABLES
    FONDO_MANTENIMIENTO = global_config.maintainance_fund  # UNIDADES REAJUSTABLES

    # print(f"{VALOR_UR} * {COSTO_CUARTO_UR[socio.bedrooms-2]} = {VALOR_UR * ((COSTO_CUARTO_UR[socio.bedrooms-2]))}")
    return VALOR_UR * ((COSTO_CUARTO_UR[socio.bedrooms-2])) #+ FONDO_MANTENIMIENTO)
