# Test input files and expected clients

The `test_inputs` directory contains the different types of OpenAPI JSON files' sources.

The `test_openapi_petstore_file.json` file is generated from Swagger UI preset data (Found under 'Edit > Load Petstore OAS 3.0', [here](https://editor.swagger.io/))

The expected result/client from the `test_input.py` FASTApi app is generated on the fly as the tests starts running (see `conftest.py`).

The expected result/client from the `test_openapi_petstore_file.json` is generated using the below command and reviewed by us, making sure that what is generated complies with what we support.

```shell
python -m python_client_generator --open-api input_openapi_petstore_file.json --package-name test_project --project-name test-project --outdir clients
```
