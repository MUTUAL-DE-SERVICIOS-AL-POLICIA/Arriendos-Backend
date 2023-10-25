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


def Make_Rental_Form(request, rental_id):

    serializer_class = RentalsSerializer
    rental = rental_id
    rental =  Rental.objects.get(pk=rental)
    serializer = serializer_class(rental)
    rental = serializer.data

    customer = rental.get("customer")
    customer_id = customer.get("id")
    customer_type = customer.get("customer_type")
    customer_type_name = customer_type.get("name")
    contacts = customer.get("contacts")

    if customer.get("institution_name") is None:
        customers = customer.get("contacts")
        for customer in customers:
            name = customer.get("name")
            nit = customer.get("ci_nit")

    else:
        name = customer.get("institution_name")
        nit = customer.get("nit")

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

    ruta_archivo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reserva.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="formulariodesolicitudreserva.pdf"'
    if os.path.exists(ruta_archivo_html):

        with open(ruta_archivo_html, 'r', encoding='utf-8') as archivo_html:
                html_content = archivo_html.read()

    html_string = render_to_string('reserva.html', {
        'num':num,
        'name': name,
        'nit': nit,
        'selected_products':selected_products,
        'initial_total': rental.get("initial_total"),
        'contacts': contacts,
        'requirements': requirements,
        'rental': rental_id
        })

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(
        string='@page { margin-left: 2cm; margin-right: 1cm; margin-top: 2cm; margin-bottom: 1.5cm; }'
        )])
    return response