# coding: utf-8

"""
    Optimeering

"""  # noqa: E501
from typing import Dict, List, Optional, Tuple, Union

from optimeering.api_client import OptimeeringClient, RequestSerialized
from optimeering.logger import log_function_timing, suggest_series_id_optimization
from optimeering.models.access_key_created import AccessKeyCreated
from optimeering.models.access_key_post_response import AccessKeyPostResponse
from optimeering.models.access_post_key import AccessPostKey
from pydantic import Field, StrictFloat, StrictInt, validate_call
from typing_extensions import Annotated


class AccessApi:
    """
    Collection of methods to interact with AccessApi
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = OptimeeringClient.get_default()
        self.api_client = api_client

    @validate_call
    @log_function_timing
    @suggest_series_id_optimization
    def create_api_key(
        self,
        access_post_key: AccessPostKey,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]],
        ] = None,
    ) -> AccessKeyPostResponse:
        """Post Access

        Creates a new access key

        :param access_post_key: (required)
        :type access_post_key: AccessPostKey
        :return: Returns the result object.
        :rtype: AccessKeyPostResponse

        :Example:

                >>> from optimeering import Configuration, OptimeeringClient
                >>> configuration = Configuration(host="https://app.optimeering.com")
                >>> client = OptimeeringClient(configuration=configuration)
                >>> # Post data point - replace ... with correct dataformat documented above
                >>> response = client.access_api.create_api_key(...)

        """  # noqa: E501

        _param = self._create_api_key_serialize(
            access_post_key=access_post_key,
        )

        _response_types_map: Dict[str, Optional[str]] = {
            "200": "AccessKeyPostResponse",
            "422": "HTTPValidationError",
        }

        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        response = self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data
        return response

    def _create_api_key_serialize(
        self,
        access_post_key,
    ) -> RequestSerialized:
        _collection_formats: Dict[str, str] = {}

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if access_post_key is not None:
            _body_params = access_post_key

        return self.api_client.param_serialize(
            method="POST",
            resource_path="/api/access/apikey/create",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            collection_formats=_collection_formats,
        )

    @validate_call
    @log_function_timing
    @suggest_series_id_optimization
    def delete_key(
        self,
        id: StrictInt,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]],
        ] = None,
    ) -> bool:
        """Drop Key

        Deletes an api key.

        :param id: (required)
        :type id: int
        :return: Returns the result object.
        :rtype: bool

        :Example:

                >>> from optimeering import Configuration, OptimeeringClient
                >>> configuration = Configuration(host="https://app.optimeering.com")
                >>> client = OptimeeringClient(configuration=configuration)
                >>> # Post data point - replace ... with correct dataformat documented above
                >>> response = client.access_api.delete_key(...)

        """  # noqa: E501

        _param = self._delete_key_serialize(
            id=id,
        )

        _response_types_map: Dict[str, Optional[str]] = {
            "200": "bool",
            "422": "HTTPValidationError",
        }

        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        response = self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data
        return response

    def _delete_key_serialize(
        self,
        id,
    ) -> RequestSerialized:
        _collection_formats: Dict[str, str] = {}

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if id is not None:
            _query_params.append(("id", id))

        # process the header parameters
        # process the form parameters
        # process the body parameter

        return self.api_client.param_serialize(
            method="DELETE",
            resource_path="/api/access/apikey/delete",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            collection_formats=_collection_formats,
        )

    @validate_call
    @log_function_timing
    @suggest_series_id_optimization
    def list_my_keys(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]],
        ] = None,
    ) -> List[AccessKeyCreated]:
        """Get Access

        Lists all the keys owned by the user.

        :return: Returns the result object.
        :rtype: List[AccessKeyCreated]

        :Example:

                >>> from optimeering import Configuration, OptimeeringClient
                >>> configuration = Configuration(host="https://app.optimeering.com")
                >>> client = OptimeeringClient(configuration=configuration)
                >>> # Get filtered data point - replace ... with appropriate filters documented above
                >>> response = client.access_api.list_my_keys(...)

        """  # noqa: E501

        _param = self._list_my_keys_serialize()

        _response_types_map: Dict[str, Optional[str]] = {
            "200": "List[AccessKeyCreated]",
        }

        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        paginated_response = self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data
        next_page = paginated_response.next_page

        if next_page is None:
            return paginated_response

        # resolve extendable attribute
        attribute_to_extend_selected: Optional[str] = None
        if "series_id" in set(paginated_response.items[0].model_fields):
            extendable_attribute = {"datapoints", "events"}
            attribute_to_extend = extendable_attribute.intersection(set(paginated_response.items[0].model_fields))
            if len(attribute_to_extend) == 1:
                attribute_to_extend_selected = list(attribute_to_extend)[0]
            else:
                raise AttributeError("Failed to resolve extendable attribute.")

        while next_page is not None:
            next_pagination = self.api_client.call_api(
                method=_param[0],
                url=next_page,
                header_params=_param[2],
                body=_param[3],
                post_params=_param[4],
                _request_timeout=_request_timeout,
            )
            next_pagination.read()
            next_pagination = self.api_client.response_deserialize(
                response_data=next_pagination,
                response_types_map=_response_types_map,
            ).data
            next_page = next_pagination.next_page

            if attribute_to_extend_selected:
                if next_pagination.items[0].series_id == paginated_response.items[-1].series_id:
                    # if series id is same, extract the first item and extend to last item
                    continued_data: List = getattr(next_pagination.items.pop(0), attribute_to_extend_selected)
                    previous_data: List = getattr(paginated_response.items[-1], attribute_to_extend_selected)
                    previous_data.extend(continued_data)
            paginated_response.items.extend(next_pagination.items)

        return paginated_response

    def _list_my_keys_serialize(
        self,
    ) -> RequestSerialized:
        _collection_formats: Dict[str, str] = {}

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter

        return self.api_client.param_serialize(
            method="GET",
            resource_path="/api/access/apikey/list_my_keys",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            collection_formats=_collection_formats,
        )
