# blog/rpc/xmlrpc.py
# Carson Gee
# 2010 July 13
# http://carsongee.com
# 
# based on Greg Abbas' adaptation of Amit Upadhyay's xmlrpc implementation
# http://www.allyourpixel.com/site_media/src/xmlrpc.py.txt
# http://nerdierthanthou.nfshost.com/2005/09/xmlrpc-support-for-django.html
# 
# My modifications include:
#
# Fixed bug for Python >= 2.5 compatibility
# Added registered function for MovableType's supportedMethods call

import sys
import traceback
import SimpleXMLRPCServer
from django.http import HttpResponseServerError, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def public(f):
    f.public = True
    return f

def is_public(func):
    return func is not None and hasattr(func, 'public') and func.public

def dotify(name):
    return name.replace('_','.')

def list_public_methods(obj):
    """Returns a list of attribute strings, found in the specified
    object, which represent callable attributes"""

    methods = SimpleXMLRPCServer.list_public_methods(obj)
    methods = [dotify(m) for m in methods if is_public(getattr(obj, m, None))]
    return methods

def resolve_dotted_attribute(obj, attr, allow_dotted_names=True):
    """resolve_dotted_attribute(a, 'b.c.d') => a.b.c.d

    Similar to the one in SimpleXMLRPCServer, except that it tries
    converting dots to underscores, too.
    """
    
    attrs = attr.split('.')
    
    if attrs[0].startswith('_'):
        raise AttributeError('attempt to access private attribute "%s"' % i)
    for i in range(len(attrs),0,-1):
        name = '_'.join(attrs[:i])
        obj0 = getattr(obj, name, None)
        #print '%r %r -> %r' % (obj, name, obj0)
        if obj0:
            attrs = attrs[i:]
            if len(attrs):
                obj0 = resolve_dotted_attribute(
                    obj0, '.'.join(attrs), allow_dotted_names)
            return obj0
        if not allow_dotted_names:
            return None

class SafeXMLRPCView(SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    """ class SafeXMLRPCView

        Checks for "public" attribute on callables before calling them.    
    """
    def system_listMethods(self):
        """system.listMethods() => ['add', 'subtract', 'multiple']

        Returns a list of the methods supported by the server."""

        methods = self.funcs.keys()
        if self.instance is not None:
            # Instance can implement _listMethods to return a list of
            # methods
            if hasattr(self.instance, '_listMethods'):
                methods = SimpleXMLRPCServer.remove_duplicates(
                        methods + self.instance._listMethods()
                    )
            # if the instance has a _dispatch method then we
            # don't have enough information to provide a list
            # of methods
            elif not hasattr(self.instance, '_dispatch'):
                methods = SimpleXMLRPCServer.remove_duplicates(
                        methods + list_public_methods(self.instance)
                    )
        methods.sort()
        return methods

    system_listMethods.public = True
    
    def system_methodSignature(self, method_name):
        return SimpleXMLRPCView.system_methodSignature(self, method_name)
    system_methodSignature.public = True

    def system_methodHelp(self, method_name):
        return SimpleXMLRPCView.system_methodHelp(self, method_name)
    system_methodHelp.public = True
    
    def _dispatch(self, method, params):
        """Dispatches the XML-RPC method.

            Overwriting to put some extra checks before calling a method. 
            
            It I get mt.supportedMethods, then do system_listMethods.
        """

        if method == "mt_supportedMethods" or method == "mt.supportedMethods":
            return self.system_listMethods()

        func = None
        try:
            # check to see if a matching function has been registered
            func = self.funcs[method]
        except KeyError:
            if self.instance is not None:
                # check for a _dispatch method
                if hasattr(self.instance, '_dispatch'):
                    return apply(
                        getattr(self.instance,'_dispatch'),
                        (method, params)
                        )
                else:
                    # call instance method directly
                    try:
                        func = resolve_dotted_attribute(self.instance, method)
                    except AttributeError:
                        pass

        if func is not None and hasattr(func, 'public') and func.public:
            return apply(func, params)
        else:
            raise Exception('method "%s" is not supported' % method)

@csrf_exempt
def view(request, module):
    #print(request.raw_post_data)
    if sys.version_info[:3] >= (2,5,):
        dispatcher = SafeXMLRPCView(allow_none=False, encoding=None)
    else:
        dispatcher = SafeXMLRPCView()
    
    try:
        mod = __import__(module, '', '', [''])
    except ImportError, e:
        raise EnvironmentError, "Could not import module '%s' (is it on sys.path?): %s" % (module, e)
    
    dispatcher.register_instance(mod)
    dispatcher.register_introspection_functions()

    try:
        if request.META['REQUEST_METHOD'] != 'POST':
            raise Exception('Non POST methods not allowed.')
    
        # get arguments
        data = request.raw_post_data
        response = dispatcher._marshaled_dispatch(
                data, getattr(mod, '_dispatch', None)
            )
    except:
        #traceback.print_exc()
        # internal error, report as HTTP server error
        response = SimpleXMLRPCServer.xmlrpclib.dumps(
            SimpleXMLRPCServer.xmlrpclib.Fault(1, "%s:%s" % (
                    sys.exc_type, sys.exc_value))
        )
    #print(response)
    return HttpResponse(response, mimetype="text/xml")

