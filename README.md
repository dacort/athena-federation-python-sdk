# (Unofficial) Python SDK for Athena Federation

This is an _unofficial_ Python SDK for Athena Federation.

## Local Development

- Ensure you've got the `build` module install and SDK dependencies.

```
pip install build
pip install -r requirements.txt
```

- Now make a wheel.

```shell
python -m build
```

This will create a file in `dist/`: `dist/unoffical_athena_federation_sdk-0.0.0-py3-none-any.whl`

Copy that file to your example repo and you can include it in your `requirements.txt` like so:

```
unoffical-athena-federation-sdk @ file:///unoffical_athena_federation_sdk-0.0.0-py3-none-any.whl
```