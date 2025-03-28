# coding: utf-8

"""
    Optimeering

"""  # noqa: E501

import copy
import http.client as httplib
import logging
import multiprocessing
import sys
from logging import FileHandler
from typing import Optional, Union
from urllib.parse import urlparse

import urllib3

JSON_SCHEMA_VALIDATION_KEYWORDS = {
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "maxLength",
    "minLength",
    "pattern",
    "maxItems",
    "minItems",
}


class Configuration:
    """This class is used to configure the :any:`OptimeeringClient`.

    :param host: API host url.
    :param api_auth_url: URL for Authentication. Defaults to `api://{host}/.default`
    :param retries:
        Number of retries for API requests.
        Also supports a urllib ``Retry`` object. `See the urlib docs <https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry>`_
    :param api_key: API Key to use for Authentication.
    :param token: Token to use for Authentication. Only use this when you don't want to have the :any:`OptimeeringClient` retrieve a token.

    :Example:

    >>> from optimeering import Configuration, OptimeeringClient
    >>> configuration = Configuration(host="https://app.optimeering.com")

    :API Key Example:

    >>> from optimeering import Configuration, OptimeeringClient
    >>> configuration = Configuration(host="https://app.optimeering.com", api_key="your api key")

    :Token Example:

    >>> from optimeering import Configuration, OptimeeringClient
    >>> configuration = Configuration(host="https://app.optimeering.com", token="your token")
    """

    _default = None

    def __init__(
        self,
        host: Optional[str] = "https://app.optimeering.com",
        api_auth_url: Optional[str] = None,
        *,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        retries: Optional[Union[int, urllib3.Retry]] = None,
        debug: Optional[bool] = None,
    ) -> None:
        """Constructor"""
        self._base_path = "http://localhost" if host is None else host
        self.api_auth_url = (
            f"api://{urlparse(self._base_path).netloc}/.default" if api_auth_url is None else api_auth_url
        )

        # Check auth conflict
        auth_parameters = (api_key, token)
        if sum((auth_param is not None) for auth_param in auth_parameters) > 1:
            raise Exception("Only a single mode of authorization can be used.")

        self.api_key = api_key
        self.token = token

        self.logger = {}
        """Logging Settings
        """
        self.logger["package_logger"] = logging.getLogger("optimeering")
        self.logger["urllib3_logger"] = logging.getLogger("urllib3")
        self.logger_format = "%(asctime)s %(levelname)s %(message)s"
        """Log format
        """
        self.logger_stream_handler = None
        """Log stream handler
        """
        self.logger_file_handler: Optional[FileHandler] = None
        """Log file handler
        """
        self.logger_file = None
        """Debug file location
        """
        if debug is not None:
            self.debug = debug
        else:
            self.__debug = False
        """Debug switch
        """

        self.verify_ssl = True
        """SSL/TLS verification
           Set this to false to skip verifying SSL certificate when calling API
           from https server.
        """
        self.ssl_ca_cert = None
        """Set this to customize the certificate file to verify the peer.
        """
        self.cert_file = None
        """client certificate file
        """
        self.key_file = None
        """client key file
        """
        self.assert_hostname = None
        """Set this to True/False to enable/disable SSL hostname verification.
        """
        self.tls_server_name = None
        """SSL/TLS Server Name Indication (SNI)
           Set this to the SNI value expected by the server.
        """

        self.connection_pool_maxsize = multiprocessing.cpu_count() * 5
        """urllib3 connection pool's maximum number of connections saved
           per pool. urllib3 uses 1 connection as default value, but this is
           not the best value when you are making a lot of possibly parallel
           requests to the same host, which is often the case here.
           cpu_count * 5 is used as default value to increase performance.
        """

        self.proxy: Optional[str] = None
        """Proxy URL
        """
        self.proxy_headers = None
        """Proxy headers
        """
        self.retries = retries
        """Adding retries to override urllib3 default value 3
        """
        # Enable client side validation
        self.client_side_validation = True

        self.socket_options = None
        """Options to pass down to the underlying urllib3 socket
        """

        self.datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        """datetime format
        """

        self.date_format = "%Y-%m-%d"
        """date format
        """

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ("logger", "logger_file_handler"):
                setattr(result, k, copy.deepcopy(v, memo))
        # shallow copy of loggers
        result.logger = copy.copy(self.logger)
        # use setters to configure loggers
        result.logger_file = self.logger_file
        result.debug = self.debug
        return result

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

    @classmethod
    def set_default(cls, default):
        """Set default instance of configuration.

        It stores default configuration, which can be
        returned by get_default_copy method.

        :param default: object of Configuration
        """
        cls._default = default

    @classmethod
    def get_default_copy(cls):
        """Deprecated. Please use `get_default` instead.

        Deprecated. Please use `get_default` instead.

        :return: The configuration object.
        """
        return cls.get_default()

    @classmethod
    def get_default(cls):
        """Return the default configuration.

        This method returns newly created, based on default constructor,
        object of Configuration class or returns a copy of default
        configuration.

        :return: The configuration object.
        """
        if cls._default is None:
            cls._default = Configuration()
        return cls._default

    @property
    def logger_file(self):
        """The logger file.

        If the logger_file is None, then add stream handler and remove file
        handler. Otherwise, add file handler and remove stream handler.

        :type: str
        """
        return self.__logger_file

    @logger_file.setter
    def logger_file(self, value):
        """The logger file.

        If the logger_file is None, then add stream handler and remove file
        handler. Otherwise, add file handler and remove stream handler.

        :param value: The logger_file path.
        :type: str
        """
        self.__logger_file = value
        if self.__logger_file:
            # If set logging file,
            # then add file handler and remove stream handler.
            self.logger_file_handler = logging.FileHandler(self.__logger_file)
            self.logger_file_handler.setFormatter(self.logger_formatter)
            for _, logger in self.logger.items():
                logger.addHandler(self.logger_file_handler)

    @property
    def debug(self):
        """Debug status"""
        return self.__debug

    @debug.setter
    def debug(self, value):
        """Debug status

        :param value: The debug status, True or False.
        :type: bool
        """
        self.__debug = value
        if self.__debug:
            # if debug status is True, turn on debug logging
            for _, logger in self.logger.items():
                logger.setLevel(logging.DEBUG)
            # turn on httplib debug
            httplib.HTTPConnection.debuglevel = 1
        else:
            # if debug status is False, turn off debug logging,
            # setting log level to default `logging.WARNING`
            for _, logger in self.logger.items():
                logger.setLevel(logging.WARNING)
            # turn off httplib debug
            httplib.HTTPConnection.debuglevel = 0

    @property
    def logger_format(self):
        """The logger format.
        The logger_formatter will be updated when sets logger_format.
        """
        return self.__logger_format

    @logger_format.setter
    def logger_format(self, value):
        """The logger format.

        The logger_formatter will be updated when sets logger_format.

        :param value: The format string.
        :type: str
        """
        self.__logger_format = value
        self.logger_formatter = logging.Formatter(self.__logger_format)

    def to_debug_report(self):
        """Gets the essential information for debugging.

        :return: The report for debugging.
        """
        return (
            "Python SDK Debug Report:\n"
            "OS: {env}\n"
            "Python Version: {pyversion}\n"
            "Version of the API: 0.1.0\n"
            "SDK Package Version: 0.0.1".format(env=sys.platform, pyversion=sys.version)
        )

    @property
    def host(self) -> str:
        return self._base_path
