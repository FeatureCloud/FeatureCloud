# Instruction to release the pip package (for FC core team)
Here we describe how FC core team can update the pip package on Pypi.

## [setup.py](/setup.py)
All the packages should be listed in the packages.
Only two entrypoints are defined, `featurecloud` and `FeatureCloud`, which are connected 
to [fc_command](/FeatureCloud/__main__.py').

The version number can be manually set in the setup.py file.

## Updating the pip package
For updating the pip package you need an account in [https://pypi.org/](https://pypi.org/). For testing the pip package,
it better to creat an account in [https://test.pypi.org/](https://test.pypi.org/) and upload the repo there.
For updating the repo, your account should be added to the list of owners.
For creating the package you should install `setuptools` and for uploading the package you should install `twine`, 
which asks for your username and password. 
### steps
1. Call this:
```python setup.py sdist```
2. then in the dist folder there will be a FeatureCloud-....tar.gz file. Install it using:
```pip install dist/FeatureCloud...tar.gz```
3. Then it should work. You can test it by calling ```featurecloud --help``` which gives a list supported commands

NOTICE: If you are installing the same version, do not forget to uninstall it first!

4. To upload it to pypi test:
```twine upload --repository testpypi dist/FeatureCloud-....tar.gz```

5. For uploading it to pypi:
```twine upload dist/FeatureCloud-....tar.gz```
