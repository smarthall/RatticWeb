from django.core.exceptions import ValidationError
from urlparse import urlparse

import re


class BaseSchemeValidator(object):
    valid_schemes = []

    def __call__(self, uri):
        # If we are being called this way, parse the URL first
        self.validate(urlparse(uri))

    def validate(self, split_uri):
        # Split the path up
        (scheme, netloc, path, params, query, fragment) = split_uri

        # Validate pieces
        self.validate_scheme(scheme)
        self.validate_netloc(netloc)
        self.validate_path(path)
        self.validate_params(params)
        self.validate_query(query)
        self.validate_fragment(fragment)

        # Validate overall
        self.validate_uri(tuple)

    def validate_scheme(self, scheme):
        if scheme in self.valid_schemes:
            raise ValidationError('"%s" is not a valid scheme for this validator' % scheme)

    def validate_netloc(self, netloc):
        pass

    def validate_path(self, path):
        pass

    def validate_params(self, params):
        pass

    def validate_query(self, query):
        pass

    def validate_fragment(self, fragment):
        pass

    def validate_uri(self, split_uri):
        pass


class HostAuthorityValidationMixin:
    netloc_splitter = re.compile(
        r'^((?P<userinfo>[^@]+)@)?'  # User info
        r'(?P<host>[^:]+)'           # Host
        r'(:(?P<port>\d+))?$'        # Port
    )

    def validate_userinfo(self, userinfo):
        # This should be validated elsewhere
        pass

    def validate_host(self, host):
        pass

    def validate_port(self, port):
        try:
            port = int(port, 10)
        except ValueError:
            raise ValidationError('The port does not appear to be a number')

        if port < 0 or port > 65536:
            raise ValidationError('Port number out of range')

    def validate_netloc(self, netloc):
        # Check for validity
        match = self.netloc_splitter.search(netloc)
        if not match:
            raise ValidationError('Could not validate the authority section of the URI')

        # Get components
        (userinfo, host, port) = match.group('userinfo', 'host', 'port')

        # Validate Components
        self.validate_host(host)
        if userinfo is not None:
            self.validate_userinfo(userinfo)
        if port is not None:
            self.validate_port(port)
        print userinfo, host, port


class HTTPValidator(HostAuthorityValidationMixin, BaseSchemeValidator):
    pass


class URIValidator(object):
    scheme_validators = {
        'http': HTTPValidator(),
        'https': HTTPValidator(),
    }

    def __init__(self, enabled_schemes=None):
        if enabled_schemes is None:
            self.enabled_schemes = self.scheme_validators.keys()
        else:
            self.enabled_schemes = enabled_schemes

    def __call__(self, uri):
        # Get the components of the URI
        split_uri = urlparse(uri)

        # Get the scheme
        scheme = split_uri.scheme

        # If its not in the whitelist
        if scheme not in self.enabled_schemes:
            raise ValidationError('Scheme "%s" is not allowed' % scheme)

        # Choose the right validator
        validator = self.scheme_validators.get(scheme, None)

        # If there is no validator raise an exception
        if validator is None:
            raise ValidationError('No validator is available for scheme "%s"' % scheme)

        # Run the validator
        validator.validate(split_uri)
