from django.urls import reverse


def sidebar_menu(request):

    if not request.user.is_authenticated:
        return {"sidebar_menu": []}

    if request.user.is_superuser:
        perfil = None
    else:
        perfil = request.user.perfil

    menu = []

    # ============================
    # Dashboard
    # ============================

    if request.user.is_superuser or perfil.dashboard:

        menu.append({
            "titulo": "Dashboard",
            "icono": "📊",
            "url": reverse("dashboard:home"),
        })

    # ============================
    # Finanzas
    # ============================


    if request.user.is_superuser or perfil.finanzas:
        
            menu.append({
                    "titulo": "Cuentas por pagar",
                    "icono": "💳",
                    "url": reverse("compras:cuenta_list"),
        
                })

     # ============================
        # Servicios
        # ============================

    if request.user.is_superuser or perfil.administracion:

            menu.append({
                "titulo": "Servicios recurrentes",
                "icono": "  💳",

                "submenu": [
                    
                    {
                        "titulo": "Registrar servicio",
                        "url": reverse("servicios:create"),
                    },

                    {
                        "titulo": "Servicios pendientes",
                        "url": reverse("servicios:pendientes"),
                    },
                    {
                        "titulo": "Servicios recurrentes",
                        "url": reverse("servicios:list"),
                    }
                ]
                
                
            })

    if request.user.is_superuser or perfil.administracion:

        menu.append({

            "titulo": "Sucursales",
            "icono": "👥",

            "submenu": [
                 
                 {
                    "titulo": "Todas",
                    "url": reverse("sucursales:list"),
                },

            

            ]

        })




    # ============================
    # Ventas
    # ============================

    if request.user.is_superuser or perfil.ventas:

        menu.append({

            "titulo": "Resumen del día",
            "icono": "🏪",

            "submenu": [
                {
                    "titulo": "Registrar venta",
                    "url": reverse("ventas:venta_diaria_create"),
                },
                {
                    "titulo": "Registrar inventario",
                    "url": reverse("inventario:inventario_diario"),
                },



            ]

        })


    if request.user.is_superuser or perfil.administracion:
    
            menu.append({
    
                "titulo": "Ventas",
                "icono": "🏪",
    
                "submenu": [
                    {
                        "titulo": "Registrar venta",
                        "url": reverse("ventas:venta_diaria_create"),
                    },
    
                    {
                        "titulo": "Ventas diarias",
                        "url": reverse("ventas:venta_diaria_list"),
                    },
    
    
    
                ]
    
            })

    # ============================
    # Inventario
    # ============================

    if request.user.is_superuser or perfil.inventario:

        menu.append({

            "titulo": "Inventario",
            "icono": "📦",

            "submenu": [

                {
                    "titulo": "Productos",
                    "url": reverse("inventario:producto_list"),
                },
                {
                    "titulo": "Inventario diario",
                    "url": reverse("inventario:inventario_diario"), 

                },
                {
                    "titulo": "Historico de inventario diario",
                    "url": reverse("inventario:inventario_list"), 
                }

            ]

        })

    # ============================
    # Finanzas
    # ============================

    if request.user.is_superuser or perfil.finanzas or perfil.gastos:

        menu.append({

            "titulo": "Gastos",
            "icono": "💰",

            "submenu": [

                {
                    "titulo": "Crear",
                    "url": reverse("gastos:create"),
                },

                {
                    "titulo": "Listado",
                    "url": reverse("gastos:list"),
                },

                {
                    "titulo": "Categorías",
                    "url": reverse("gastos:categoria_list"),
                },

                {
                    "titulo": "Servicios recurrentes",
                    "url": reverse("servicios:list"),
                },

            ]

        })

    # ============================
    # Nómina
    # ============================

    if request.user.is_superuser or perfil.nomina:

        menu.append({

            "titulo": "Nómina",
            "icono": "👥",

            "submenu": [
                 
                 {
                    "titulo": "Pendiente",
                    "url": reverse("nomina:pendientes"),
                },

                {
                    "titulo": "Historial",
                    "url": reverse("nomina:historial"),
                },

                {
                    "titulo": "Empleados",
                    "url": reverse("nomina:empleado_list"),
                },

            ]

        })

    return {
        "sidebar_menu": menu
    }