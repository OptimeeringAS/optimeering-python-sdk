import inspect
import unittest.mock
from unittest import TestCase

import optimeering
import polars as pl  # type: ignore[import-untyped]
import pyarrow as pa  # type: ignore[import-untyped]
from optimeering import Configuration, OptimeeringClient
from optimeering.azure_authentication import AzureAuth
from optimeering.rest import RESTClientObject, RESTResponse
from tests.data_mocks import FakeResponse, generate_data

config = Configuration(host="Testurlhere")
client = OptimeeringClient(config)
_ = pl
_ = pa


class TestGeneratedClient(TestCase):
    def setUp(self):
        self.mock_azure = unittest.mock.patch.object(AzureAuth, "get_token", return_value=None)
        self.mock_azure.start()

    def tearDown(self):
        self.mock_azure.stop()

    def test_api_series_and_single_datapoint(self):
        """Tests calling series and getting one datapoint"""
        apis_to_test = {
            k: v
            for k, v in optimeering.api.__dict__.items()
            if k.endswith("Api") and v.__module__.startswith("optimeering.api")
        }

        for api_name in apis_to_test:
            api = getattr(optimeering, api_name)(api_client=client)

            # get series
            for method in [i[0] for i in inspect.getmembers(api) if i[0].endswith("series")]:
                api_method = getattr(api, method)
                response_model_type = inspect.signature(api_method).return_annotation
                data = generate_data(response_model_type.__name__)
                with unittest.mock.patch.object(
                    RESTClientObject, "request", return_value=RESTResponse(FakeResponse(data))
                ):
                    response = api_method()

                # get datapoints
                response_model_type = eval(inspect.signature(response.datapoints).return_annotation)

                data = generate_data(response_model_type.__name__)
                with unittest.mock.patch.object(
                    RESTClientObject, "request", return_value=RESTResponse(FakeResponse(data))
                ):
                    datapoints = response.datapoints()
                assert len(datapoints.to_polars(unpack_value_method="retain_original")) > 0
                assert len(datapoints.to_polars(unpack_value_method="new_columns")) > 0
                assert len(datapoints.to_polars(unpack_value_method="new_rows")) > 0
