from django.urls import reverse


from django.urls import reverse


def sidebar_menu(request):

    return {

        "sidebar_menu": [

            {
                "titulo": "Dashboard",
                "icono": "📊",
                "url": reverse("dashboard:home"),
            },

            {
                "titulo": "Pagos pendientes",
                "icono": "🏪",
                "url": reverse("servicios:pendientes"),
            },

            {
                "titulo": "Ventas",
                "icono": "🏪",
                "url": reverse("resumen_list"),
            },
            {
                "titulo": "Proveedores",
                "icono": "🏪",
                "submenu": [
                    {
                        "titulo": "Crear",
                        "url": reverse("compras:proveedor_create"),
                    },

                    {
                        "titulo": "listado",
                        "url": reverse("compras:proveedor_list"),
                    },
                ]
            
            },

            {
                "titulo": "Sucursales",
                "icono": "🏪",
                "submenu": [
                    {
                        "titulo": "Crear",
                        "url": reverse("sucursales:create"),
                    },

                    {
                        "titulo": "listado",
                        "url": reverse("sucursales:list"),
                    },
                ]
            },

            {
                "titulo": "Inventario",
                "icono": "📦",
                "submenu": [

                    # Más adelante...
                    # {"titulo": "Productos", "url": reverse(...)},
                    # {"titulo": "Categorías", "url": reverse(...)},

                ]
            },

            {
                "titulo": "Gastos",
                "icono": "💰",
                "submenu": [
                    {
                        "titulo": "Crear",
                        "url": reverse("gastos:create"),
                    },

                    {
                        "titulo": "listado",
                        "url": reverse("gastos:list"),
                    },
                    

                    {
                        "titulo": "Categorías de gasto",
                        "url": reverse("gastos:categoria_list"),
                    },

                ]
                
            },

            {
                "titulo": "Nómina",
                "icono": "👥",
                "submenu": [

                    {
                        "titulo": "Nóminas pendientes",
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
            },

            {
                "titulo": "Servicios",
                "icono": "📅",
                "submenu": [
                    {
                        "titulo": "Crear",
                        "url": reverse("servicios:create"),
                    },

                    {
                        "titulo": "listado",
                        "url": reverse("servicios:list"),
                    },

                ]
            },

        ]
    }