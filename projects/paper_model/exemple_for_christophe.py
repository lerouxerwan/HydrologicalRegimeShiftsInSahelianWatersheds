def compute_ke(P: float, C: float, p_init: float, p_0max: float, a: float, b: float, Ke_max: float, skc: float) -> float:
    """
    P correspond à la valeur de precipitation annuelle
    C correspond à la valeur d'état du modèle
    Le reste des paramètres sont des paramètres du modèle
    """
    p_0 = p_init + C * (p_0max - p_init)
    ratio = (P ** a) / (P ** a + p_0 ** a)
    ke_l = (ratio ** b) * Ke_max
    return ke_l / skc