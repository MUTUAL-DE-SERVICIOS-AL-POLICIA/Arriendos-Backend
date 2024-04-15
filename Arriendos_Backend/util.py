import os
from django.template.loader import render_to_string
from weasyprint import HTML,CSS
from django.http import HttpResponse
from datetime import datetime

def required_fields(request, required_fields):
    missing_fields = [field for field in required_fields if field not in request.data]
    if missing_fields:
        return {
            'error': 'missing required fields',
            'missing required fields': missing_fields
        }
    return None

def generate_pdf(html, params):
    root_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.jpg')
    params["logo"]='file://' + root_logo
    params["date"]=datetime.now().strftime("%d/%m/%y")
    html_content = render_to_string(html, params)
    html = HTML(string=html_content)
    css = CSS(string='@page { margin-top: 0px; margin-bottom: 20mm; margin-left: 20mm; margin-right: 20mm; }')
    pdf_file = html.write_pdf(stylesheets=[css])
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="hello_world.pdf"'
    return response
