from django.shortcuts import render
from django.http import HttpResponse
from leases.models import Rental
from leases.serializer import RentalsSerializer
from .models import Warranty_Movement
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
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
    director = "Cnl. MSc. CAD. LUCIO ENRIQUE RENÉ JIMÉNEZ VARGAS"
    customer = rental.get("customer")
    contacts = customer.get("contacts")
    customers = customer.get("contacts")
    for customer in customers:
        name = customer.get("name")
        nit = customer.get("ci_nit")
    
    selected_products = rental.get("selected_products")
    now = timezone.now()
    formatted_date = DateFormat(now).format(get_format('DATE_FORMAT'))

    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    month = month_names[now.month]
   
    formatted_date = now.strftime(f"%d de {month} de %Y")
    warranty = Warranty_Movement.objects.filter(rental_id=rental_id).latest('id')
    
    ruta_archivo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solicitud_devolucion_de_garantia.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="solicitud_devolucion_de_garantia.pdf"'
    if os.path.exists(ruta_archivo_html):

        with open(ruta_archivo_html, 'r', encoding='utf-8') as archivo_html:
                html_content = archivo_html.read()

    html_string = render_to_string('solicitud_devolucion_de_garantia.html', {
        'name': name,
        'nit': nit,
        'director': director,
        'selected_products':selected_products,
        'contacts': contacts,
        'rental': rental_id,
        'warranty': warranty.balance,
        'date':formatted_date
        })

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(
        string='@page { margin-left: 2cm; margin-right: 1cm; margin-top: 2cm; margin-bottom: 1.5cm; }'
        )])
    return response
def Make_Damage_Warranty_Form(request, rental_id, product, mount, total, observations):
    serializer_class = RentalsSerializer

    rental = rental_id

    rental = Rental.objects.get(pk = rental_id)
    serializer = serializer_class(rental)
    rental = serializer.data

    customer = rental.get("customer")
    contacts = customer.get("contacts")
    customers = customer.get("contacts")
    for customer in customers:
        name = customer.get("name")
        nit = customer.get("ci_nit")

    selected_products_data = rental.get("selected_products")
    selected_products=[]
    for selected_product_data in selected_products_data:
        if selected_product_data["id"] == product:
            selected_product = {
                'id': selected_product_data["id"],
                'start_time': selected_product_data["start_time"],
                'product':selected_product_data["product"]
            }
            selected_products.append(selected_product)

    ruta_archivo_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ejecución_de_garantía.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="formulariodesolicitudreserva.pdf"'
    if os.path.exists(ruta_archivo_html):

        with open(ruta_archivo_html, 'r', encoding='utf-8') as archivo_html:
                html_content = archivo_html.read()

    html_string = render_to_string('ejecución_de_garantía.html', {
        'name': name,
        'nit': nit,
        'selected_products':selected_products,
        'warranty': rental.get("initial_total"),
        'contacts': contacts,
        'rental': rental_id,
        'mount': mount,
        'observations': observations,
        'product':product,
        'total':total
        })

    HTML(string=html_string).write_pdf(response, stylesheets=[CSS(
        string='@page { margin-left: 2cm; margin-right: 1cm; margin-top: 2cm; margin-bottom: 1.5cm; }'
        )])
    return response