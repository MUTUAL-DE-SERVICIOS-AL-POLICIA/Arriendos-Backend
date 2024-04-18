from django.shortcuts import render
from django.http import HttpResponse
from leases.models import Rental
from leases.serializer import RentalsSerializer
from requirements.models import Requirement
from requirements.models import Requirement_Delivered
from .models import Warranty_Movement, Event_Damage
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from datetime import datetime
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
import os
def Make_Warranty_Form(request, rental_id):
    serializer_class = RentalsSerializer
    rental = rental_id
    rental= Rental.objects.get(pk=rental)
    serializer = serializer_class(rental)
    rental = serializer.data
    contract_number = rental.get("contract_number")
    director = "Cnl. MSc. CAD. LUCIO ENRIQUE RENÉ JIMÉNEZ VARGAS"
    customer = rental.get("customer")
    contacts = customer.get("contacts")
    institution_name = customer.get("institution_name", None)
    institution_nit = customer.get("nit", None)
    customers = customer.get("contacts")
    customer = customers[0]
    name = customer.get("name")
    nit = customer.get("ci_nit")
    nup = customer.get("nup")
    if institution_name is None:
        detail_name = name
        deatil_nit = nit
    else:
        detail_name = institution_name
        deatil_nit = institution_nit
    selected_products = rental.get("selected_products")
    departments = ''
    for selected_product in selected_products:
        departments = selected_product.get("product")
        departments = departments.get("room")
        departments = departments.get("property")
    now = timezone.now()
    formatted_date = DateFormat(now).format(get_format('DATE_FORMAT'))

    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    month = month_names[now.month]
   
    request_date = now.strftime(f"%d de {month} de %Y")
    warranty = Warranty_Movement.objects.filter(rental_id=rental_id).latest('id')
    user = request.user
    today = datetime.now()
    date = today.strftime("%d/%m/%y")
    ruta_archivo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solicitud_devolucion_de_garantia.html')
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.jpg')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="solicitud_devolucion_de_garantia.pdf"'
    if os.path.exists(ruta_archivo_html):

        with open(ruta_archivo_html, 'r', encoding='utf-8') as archivo_html:
                html_content = archivo_html.read()
    customer= {
        'name': name,
        'nit': nit,
        'nup': nup,
        'institution_name': institution_name,
        'institution_nit': institution_nit,
    }

    html_string = render_to_string('solicitud_devolucion_de_garantia.html', {
        'customer':customer,
        'director': director,
        'selected_products':selected_products,
        'departments': departments,
        'contacts': contacts,
        'contract_number': contract_number,
        'warranty': warranty.balance,
        'request_date': request_date,
        'detail_name': detail_name,
        'detail_nit': deatil_nit,
        'date': date,
        'user': user,
        'logo': 'file://' + ruta_logo
        })

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(
        string='@page { margin-left: 2cm; margin-right: 1cm; margin-top: 0.2cm; margin-bottom: 2cm; }'
        )])
    return response
def Make_Damage_Warranty_Form(request, rental_id, product):
    serializer_class = RentalsSerializer

    rental = rental_id

    rental = Rental.objects.get(pk = rental_id)
    serializer = serializer_class(rental)
    rental = serializer.data
    contract_number = rental.get("contract_number")

    customer = rental.get("customer")
    contacts = customer.get("contacts")
    institution_name = customer.get("institution_name", None)
    institution_nit = customer.get("nit", None)
    customers = customer.get("contacts")
    customer = customers[0]
    name = customer.get("name")
    nit = customer.get("ci_nit")
    nup = customer.get("nup")

    selected_products_data = rental.get("selected_products")
    selected_products=[]
    for selected_product_data in selected_products_data:
        if selected_product_data["id"] == product:
            warranty_damages = Event_Damage.objects.filter(selected_product_id = selected_product_data["id"])
            event_damage_data = []
            for warranty_damage in warranty_damages:
                warranty_movement = Warranty_Movement.objects.get(pk = warranty_damage.warranty_movement_id)
                event_damage_date = timezone.localtime(warranty_damage.created_at)
                if isinstance(event_damage_date, str):
                    event_damage_date = datetime.strptime(event_damage_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                event_damage_date = event_damage_date.strftime("%d-%m-%Y %I:%M:%S %p")
                warranty_data = {
                    'mount': warranty_damage.mount,
                    'total': warranty_movement.balance,
                    'detail': warranty_movement.detail,
                    'date': event_damage_date
                }
                event_damage_data.append(warranty_data)

            selected_product = {
                'id': selected_product_data["id"],
                'start_time': selected_product_data["start_time"],
                'product':selected_product_data["product"],
                'warranty_data': event_damage_data
            }
            selected_products.append(selected_product)
    user = request.user
    today = datetime.now()
    date = today.strftime("%d/%m/%y")
    ruta_archivo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ejecucion_de_garantia.html')
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.jpg')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="formulariodeejecuciondegarantia.pdf"'
    if os.path.exists(ruta_archivo_html):

        with open(ruta_archivo_html, 'r', encoding='utf-8') as archivo_html:
                html_content = archivo_html.read()
    customer= {
        'name': name,
        'nit': nit,
        'nup': nup,
        'institution_name': institution_name,
        'institution_nit': institution_nit,
    }

    html_string = render_to_string('ejecucion_de_garantia.html', {
        'customer':customer,
        'selected_products':selected_products,
        'warranty': rental.get("initial_total"),
        'contacts': contacts,
        'contract_number': contract_number,
        'date': date,
        'user': user,
        'logo': 'file://' + ruta_logo
        })

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(
        string='@page { margin-left: 2cm; margin-right: 1cm; margin-top: 0.2cm; margin-bottom: 2cm; }'
        )])
    return response

def Make_Return_Warranty_Form(request, rental_id):
    serializer_class = RentalsSerializer
    rental = rental_id
    rental =  Rental.objects.get(pk=rental)
    serializer = serializer_class(rental)
    rental = serializer.data
    contract_number = rental.get("contract_number")

    customer = rental.get("customer")
    contacts = customer.get("contacts")
    institution_name = customer.get("institution_name", None)
    institution_nit = customer.get("nit", None)
    customers = customer.get("contacts")
    customer = customers[0]
    name = customer.get("name")
    nit = customer.get("ci_nit")
    nup = customer.get("nup")
    if institution_name is None:
        detail_name = name
        deatil_nit = nit
    else:
        detail_name = institution_name
        deatil_nit = institution_nit

    selected_products = rental.get("selected_products")
    warranty = Warranty_Movement.objects.filter(rental_id=rental_id).latest('id')
   
    requirements_data = Requirement_Delivered.objects.filter(rental_id = rental_id)
    num = len(requirements_data) +1
    requirements = []
    for requirement_data in requirements_data:
        requirement_id = requirement_data.requirement_id
        requirement = Requirement.objects.get(pk=requirement_id)

        data = {
            'name': requirement.requirement_name
        }
        requirements.append(data)
    user = request.user
    today = datetime.now()
    date = today.strftime("%d/%m/%y")
    ruta_archivo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'devolucion_de_garantia.html')
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.jpg')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="devolucion_de_garantia.pdf"'
    if os.path.exists(ruta_archivo_html):

        with open(ruta_archivo_html, 'r', encoding='utf-8') as archivo_html:
                html_content = archivo_html.read()

    html_string = render_to_string('devolucion_de_garantia.html', {
        'num':num,
        'name': name,
        'nit': nit,
        'selected_products':selected_products,
        'initial_total': rental.get("initial_total"),
        'contacts': contacts,
        'requirements': requirements,
        'contract_number': contract_number,
        'nup': nup,
        'institution_name': institution_name,
        'institution_nit': institution_nit,
        'detail_name': detail_name,
        'detail_nit': deatil_nit,
        'warranty': warranty.balance,
        'date': date,
        'user': user,
        'logo': 'file://' + ruta_logo
        })

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(
        string='@page { margin-left: 2cm; margin-right: 1cm; margin-top: 0.2cm; margin-bottom: 2cm; }'
        )])
    return response