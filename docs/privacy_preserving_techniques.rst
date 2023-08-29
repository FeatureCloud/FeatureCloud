=============================
Privacy-preserving techniques
=============================

SMPC (Secure MultiParty Computation)
------------------------------------
SMPC is a technique that allows the secure sharing of data, only making aan aggregated
version of the data visible to the coordinator.
Without SMPC, the coordinator would get data from each client.
When using SMPC, the clients split the data they have into a masked model (*data-mask*)
and the *mask* itself. The masked model and the mask then get sent to different clients.
The clients split their data as described above n times (with different masks), which is described as
the number of *shards*.


Usage
^^^^^
As with general app development as described in :doc:`getting_started`

App template based development(recommended)
"""""""""""""""""""""""""""""""""""""""""""
1. First, SMPC must be configured. Use 
   :meth:`this method <FeatureCloud.app.engine.app.AppState.configure_smpc>`
   for configuration. 
2. SMPC can now be used whenever sending data to the coordinator 
   :meth:`send_data_to_coordinator <FeatureCloud.app.engine.app.AppState.send_data_to_coordinator>`
3. As serialization might differ when data was sent using SMPC, the corresponding 
   functions gathering the data as the data must also be informed that the data
   was sent using SMPC. This affects the following methods:

   * :meth:`aggregate_data <FeatureCloud.app.engine.app.AppState.aggregate_data>`

   * :meth:`await_data <FeatureCloud.app.engine.app.AppState.await_data>`

   * :meth:`gather_data <FeatureCloud.app.engine.app.AppState.gather_data>`

Developing applications from scratch (advanced)
"""""""""""""""""""""""""""""""""""""""""""""""
To use SMPC, when sending data to the coordinator, when answering `GET /status`, 
the response must contain the smpc option. 

.. TODO: Make sure that the SMPC options are described in the API documentation

Furthermore, it should be considered that when SMPC is used, the *controller* will
aggregate data according to the `operation` option given in the status call.
Then, the ONE aggregated package will be send to the application and will be serialized
as given by `serialization`. 
*In conclusion that means that only ONE model will be posted and that model will be serialized according to `serialization`.*

.. TODO: DP
