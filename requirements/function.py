from django.shortcuts import render
from requirements.models import Requirement
from customers.models import Customer
from leases.models import Rental
from leases.serializer import RentalsSerializer
from django.http import HttpResponse
from .models import Requirement_Delivered
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
import os
from datetime import datetime
from Arriendos_Backend import util
from django.utils import timezone
import pytz


def Make_Rental_Form(request, rental_id):
    serializer_class = RentalsSerializer
    rental = rental_id
    rental =  Rental.objects.get(pk=rental)
    serializer = serializer_class(rental)
    rental = serializer.data
    contract_number = rental.get("contract_number")

    customer = rental.get("customer")
    customer_type = customer.get("customer_type")
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
    ruta_archivo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reserva.html')
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.jpg')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="formulariodesolicitudreserva.pdf"'
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
    html_string = render_to_string('reserva.html', {
        'num':num,
        'customer':customer,
        'selected_products':selected_products,
        'initial_total': rental.get("initial_total"),
        'contacts': contacts,
        'requirements': requirements,
        'contract_number': contract_number,
        'detail_name': detail_name,
        'detail_nit': deatil_nit,
        'date': date,
        'user': user,
        'logo': 'file://' + ruta_logo
        })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="formulariodesolicitudreserva.pdf"'

    base_url = request.build_absolute_uri()
    HTML(string=html_string, base_url=base_url).write_pdf(response, stylesheets=[CSS(
        string='@page { margin-left: 2cm; margin-right: 1cm; margin-top: 0.2cm; margin-bottom: 2cm; }'
    )])
    return response
