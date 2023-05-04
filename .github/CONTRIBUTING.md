# Contributing to python-client-generator

We welcome and encourage any contributions to the `python-client-generator`.

### Reporting an issue
Please check the [issue tracker](https://github.com/sennder/python-client-generator/issues) for your particular issue
or feature request before creating a new issue.

### Setting up your local environment
This project was developed using Python3.8, other python version have not been fully tested.

Install the dependencies e.g. with `poetry`:
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
