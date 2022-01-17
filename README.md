# FeatureCloud
<p align="center">
<img src="https://featurecloud.ai/assets/fc_logo_small.svg" width="400" height="400"/>
</p>

[FeatureCloud](https://featurecloud.eu/) provides a privacy-preserving platform for federated learning and data analysis.
Two major target groups who can benefit from FeatureCloud are researchers and developers. Any end-user who have data and 
want to join others in a federated collaboration can use FeatureCloud without worrying about privacy concerns.
On the other hand, developers can quickly implement a federated app and publish it in [FeatureCloud AI-store](https://featurecloud.ai/ai-store).
Using [FeatureCloud engine](https://github.com/FeatureCloud/app-template/tree/master/engine), developers can extend states to introduce new ones; for more information on developing apps, you can visit our [GitHub repository](https://github.com/FeatureCloud/app-template). For registering and testing your apps or using other apps, please visit
[FeatureCloud.ai](https://featurecloud.ai/). And for more information about FeatureCloud architecture,
please refer to 
[The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond](https://arxiv.org/abs/2105.05734) [[1]](#1).

## FeatureCloud Engine
The engine package in FeatureCloud introduces two major elements of app development: app and state. App class is responsible for registering states and transitions between them, verifying the app logic, and executing them. The app is a highly transparent component 
that requires minimum developers' familiarity. The second class, state, is where local computations carry on. Developers should 
insert their logic into states by assigning roles, adding, and taking transitions. 
## CLI
FeatureCloud provides a CLI to flexibly interact with the FeatureCloud controller, responsible for securely connecting collaborating 
clients in the FC platform. For more information about CLI, please visit our [cli](https://github.com/FeatureCloud/cli) repository. 

# INSTRUCTIONS FOR FEATURECLOUD DEVELOPERS
This part of the readme is for the FC core team, do not upload it as a readme for the pip package.
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


### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva,
O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021.
The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.
