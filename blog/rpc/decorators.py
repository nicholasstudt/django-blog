from django.contrib.auth import authenticate


def authenticated(pos=1, perm=None):
    """
    A decorator for functions that require authentication.
    Assumes that the username & password are the second & third parameters.
    """
    
    def _decorate(func):
        def _wrapper(*args, **kwargs):
            username = args[pos+0]
            password = args[pos+1]
            args = args[0:pos]+args[pos+2:]
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValueError("Authentication Failure")
            if not user.is_staff:
                raise ValueError("Authorization Failure")
            # Authorize based on perm passed in
            if perm:
                if not user.has_perm(perm):
                    raise ValueError("Authorization Failure")

            return func(user, *args, **kwargs)
        
        return _wrapper
    return _decorate
