def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header"""
    
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token