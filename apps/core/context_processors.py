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
                "titulo": "Compromisos de pago",
                "icono": "🏪",
                "url": reverse("servicios:list"),
            },

            {
                "titulo": "Ventas",
                "icono": "🏪",
                "submenu": [
                    {
                        "titulo": "Ventas",
                        "url": reverse("resumen_list"),
                    },

                    {
                        "titulo": "Crear sucursal",
                        "url": reverse("sucursales:create"),
                    },

                    {
                        "titulo": "Sucursales",
                        "url": reverse("sucursales:list"),
                    },
                ]
            },



            {
                "titulo": "Cuentas por pagar",
                "icono": "🏪",
                "submenu": [
                    
                    {
                        "titulo": "Crear",
                        "url": reverse("compras:cuenta_create"),
                    },

                    {
                        "titulo": "listado",
                        "url": reverse("compras:cuenta_list"),
                    },
                    {
                        "titulo": "Proveedores", 
                        "url": reverse("compras:proveedor_list"),
                    }
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

                    {
                        "titulo": "Servicios recurrentes",
                        "url": reverse("servicios:list"),
                    }

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

        

        ]
    }