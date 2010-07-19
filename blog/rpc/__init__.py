"""
The rpc module provides three standard remote XML-RPC interfaces for
updating, deleting, and editing the blog.

Blog API's supported:

Blogger 1.0
MetaWeblog
MovableType

As a note, Wordpress' API also works since it is just an extension of
the MovableType API, and this module safely ignores the additional
interfaces in that API.
"""
