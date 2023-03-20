# python-client-generator

Python package to generate an [httpx](https://github.com/encode/httpx)- and
[pydantic](https://github.com/pydantic/pydantic)-based async (or sync) 
client off an OpenAPI spec.

```mermaid
flowchart LR
    generator["python-client-generator"]
    app["REST API app"]
    package["app HTTP client"]

    app -- "OpenAPI json" --> generator
    generator -- "generates" --> package
```


## Using the generator

```bash
python -m python_client_generator --open-api openapi.json --package-name foo_bar --project-name foo-bar --outdir clients
```

This will produce a Python package with the following structure:
```bash
clients
├── foo_bar
│   ├── __init__.py
│   ├── apis.py
│   ├── base_client.py
│   └── models.py
└── pyproject.toml
```

### Using PATCH functions from the generator

When calling one of the generated update functions that uses an HTTP `PATCH` method, you'll
probably want to pass the additional argument `body_serializer_args={"exclude_unset": True}`. This
will ensure that only the fields that are set in the update object are sent to the API. Example:

```python
await api_client.update_contact_v1_contacts__contact_id__patch(
                body=patch_body,
                contact_id=contact.id,
                tenant=tenant,
                body_serializer_args={"exclude_unset": True}
)
```


## Contributing
Install the dependencies with `poetry`:
```shell
poetry install
```

Format the code:
```shell
make format
```

Test the code locally:
```shell
poetry run pytest
```


### Commiting

We use commitlint in the CI/CD to make sure all commit messages adhere to [conventionalcommits](https://www.conventionalcommits.org/en/v1.0.0/). See `.commitlintrc.js`, `.releaserc` and `.czrc.json` for specific implementation details.

As per the default commitlint settings for conventionalcommits ([see here](https://github.com/conventional-changelog/commitlint))
the following commit types may be used:

  - `build`
  - `chore`
  - `ci`
  - `docs`
  - `feat`
  - `fix`
  - `perf`
  - `refactor`
  - `revert`
  - `style`
  - `test`

Of which the following will cause a release (one of these types *must* be used if you are submitting code
that you expect to be deployed after merging):

  - `build`
  - `ci`
  - `docs(api)`
  - `feat`
  - `fix`
  - `perf`
  - `refactor`
  - `revert`
  
To ensure that your commits always conform to the above format, you can install `commitizen`:
```shell
npm i -g commitizen
```
