# FeatureCloud

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


### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva,
O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021.
The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.