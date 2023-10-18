def required_fields(request, required_fields):
    missing_fields = [field for field in required_fields if field not in request.data]
    if missing_fields:
        return {
            'error': 'missing required fields',
            'missing required fields': missing_fields
        }
    return None