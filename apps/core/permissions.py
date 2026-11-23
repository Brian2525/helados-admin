
def tiene_permiso_operacion(user, permiso, sucursal=None):
    """
    Valida permisos de operaciones del ERP.
    """

    if not user.is_authenticated:
        return False

    if sucursal is None:
        return False

    # Primero validar acceso a sucursal.
    # Esta función debe usar las mismas reglas
    # que SucursalPermissionMixin.
    if not usuario_puede_acceder_sucursal(user, sucursal):
        return False

    return user.has_perm(permiso)
