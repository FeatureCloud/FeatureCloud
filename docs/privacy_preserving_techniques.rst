=============================
Privacy-preserving techniques
=============================

.. _smpc anchor:

SMPC (Secure MultiParty Computation)
------------------------------------
SMPC is a technique that allows the secure sharing of data, only making an aggregated
version of the data visible to the coordinator.
Without SMPC, the coordinator gets data from each client.
When using SMPC, the clients split the data they have into multiple masked models
and masks themselves. The masked models and the masks then get sent to different clients.
The clients split their data as described above n times, which is described as
the number of **shards**. Each split gets sent to another client, so the number
of **shards** must be a number between 1 and *number_clients*.


Usage
^^^^^
As with general app development as described in :doc:`getting_started`, either
an app template can be used or development can be done from scratch.

App template based development(recommended)
"""""""""""""""""""""""""""""""""""""""""""

.. _smpc vars anchor:

1. First, SMPC must be configured. Use
:meth:`this method <FeatureCloud.app.engine.app.AppState.configure_smpc>`
for configuration. The following parameters can be set.

  * **exponent**:

    Any floating point value has to be converted to an integer and
    back, the **exponent** describes how many digits of the float are conserved
    during SMPC.
    Technically the conversion of float is the following:
    :math:`int(float \cdot 10^{exponent})`, e.g. 1035.3967 with **exponent** = 5
    gets converted to 10353 and converted back to 1035.3, meaning the loss of
    all digits after the first 5.

  * **shards**:

    decides the number of times the data is split. A value of 0 makes
    each client splits the data num_clients times.
    We recommended just using the default value (0).

  * **operation**:

    describes the operation used for aggregation of the data, see
    :meth:`the SMPCOperation variable <FeatureCloud.app.engine.app.SMPCOperation>`
    for all options. Please notice that the multiply option is still experimental.

  * **serialization**:

    describes the serialization used when sending the data,
    see all options
    :meth:`here <FeatureCloud.app.engine.app.AppState.configure_smpc>`.
    We recommended the default value.

2. SMPC can now be used whenever sending data to the coordinator with this method:
   :meth:`send_data_to_coordinator <FeatureCloud.app.engine.app.AppState.send_data_to_coordinator>`


3. As serialization of incoming data might differ when data was sent using SMPC, the corresponding
   functions gathering the data must also be informed that the data
   was sent with the corresponding serialization.
   This affects the following methods:

   * :meth:`aggregate_data <FeatureCloud.app.engine.app.AppState.aggregate_data>`

   * :meth:`await_data <FeatureCloud.app.engine.app.AppState.await_data>`

   * :meth:`gather_data <FeatureCloud.app.engine.app.AppState.gather_data>`

Developing applications from scratch (advanced)
"""""""""""""""""""""""""""""""""""""""""""""""
To use SMPC, when sending data to the coordinator, when answering *GET /status*,
the response must contain the smpc option::

  smpc: {
    operation: enum[add, multiply]
    serialization?: enum[json] // default is json
    shards?: number // default is number of participants including coordinator
    exponent?: number // default is 8
  }

See the :ref:`information in app template based development <smpc vars anchor>`
for more information on setting the variables. If shards is not given
or 0, this is interpreted as shards = number of participants including coordinator.

The data must be serialized as defined in the `serialization` variable.

Furthermore, it should be considered that when SMPC is used, the *controller* will
aggregate data according to the `operation` option given in the status call.
Then, the ONE aggregated package will be send to the application and will be serialized
as given by `serialization`.
In conclusion that means that only ONE model will be send (via the *POST /data*
request) and that model will be serialized according to *serialization*.

We suggest only giving the parameter operation and exponent. Not giving the
parameters shards and serialization will use the default values,
JSON for `serialization` and number_clients for `shards`.

.. _dp anchor:

DP (Differential Privacy)
-------------------------

Differential privacy describes a privacy enhancing technique that conceils the
contribution of each individual row of data. This is achieved by adding noise
to any numerical data sent.

Usage
^^^^^
As with general app development as described in :doc:`getting_started`, either
an app template can be used or development can be done from scratch.

App template based development(recommended)
"""""""""""""""""""""""""""""""""""""""""""
1. First, DP must be configured. Use
   :meth:`this method <FeatureCloud.app.engine.app.AppState.configure_dp>`
   for configuration. The following parameters can be set. :ref:`See here for a quick
   guide on how to choose the parameters. <parameter guide anchor>`

   * **noisetype**: describes the distribution from which noise is drawn. See
     :meth:`here <FeatureCloud.app.engine.app.AppState.configure_dp>` for all
     possible distributions.

   * **epsilon**: describes the **epsilon** privacy budget value. Please refer to
     :ref:`here <eps anchor>` for information on choosing **epsilon**

   * **delta**: describes the **delta** privacy budget value. Must be 0 for laplacian
     noise, and should be of a smaller scale than :math:`\frac{1}{numRows}`,
     where numRows is the amount of rows in the data used to train the model
     that is send out. See :ref:`here <delta anchor>` for more information.

   * **sensitivity**: describes the sensitivity of the function that was used on
     the data. See :ref:`this quide <sensClip guide anchor>`
     about how to choose the sensitivity.

   * **clippingVal**: this value describes the maximum norm of send data. This
     will be ensured by scaling the send data down so the maximum norm holds.
     This generates a fixed sensitivity and therefore can be given instead of or
     additional to the sensitivity. See :ref:`this quide <sensClip guide anchor>`
     for more information

2. DP can now be used whenever sending data to any other client:

   * :meth:`send_data_to_coordinator <FeatureCloud.app.engine.app.AppState.send_data_to_coordinator>`

   * :meth:`send_data_to_participant <FeatureCloud.app.engine.app.AppState.send_data_to_participant>`

   * :meth:`broadcast_data <FeatureCloud.app.engine.app.AppState.broadcast_data>`

3. As serialization of incoming data might differ when data was sent using DP,
   the corresponding functions gathering the data must also be informed that
   the data was sent with the corresponding serialization.
   This affects the following methods:

   * :meth:`aggregate_data <FeatureCloud.app.engine.app.AppState.aggregate_data>`

   * :meth:`await_data <FeatureCloud.app.engine.app.AppState.await_data>`

   * :meth:`gather_data <FeatureCloud.app.engine.app.AppState.gather_data>`

Developing applications from scratch (advanced)
"""""""""""""""""""""""""""""""""""""""""""""""
Please follow the general steps for developing an app as given in
:ref:`getting started <getting started dev from scratch anchor>`
However, your application should add the following parameters to the
response body of the *GET /status* request::

  dp: {
    serialization?: enum[json] // default is json
    noisetype?: enum[laplace, gauss] // default is laplace
    epsilon?: float // default is 0.99999
    delta?: float // default is 0 for laplace noise and 0.01 for gauss noise
    sensitivity?: float
    clippingVal?: float
      // default is 10.0 and only set if neither
      // clippingVal nor sensitivity are given
  }

:ref:`See here for a quick
guide on how to choose these parameters. <parameter guide anchor>`
Furthermore, data must be serialized according to the given serialization value
in the status call (JSON).

.. _parameter guide anchor:

Parameter Guide
^^^^^^^^^^^^^^^
This step by step guide goes through all needed parameters for DP and how to
set them.

.. _sensClip guide anchor:

1. **sensitivity/clippingVal**:
   DP works on the assumption that some database (a collection of rows/vectors)
   is used as input of a function. The function must output numerical data.
   In the context of FeatureCloud, the functions are usually the
   training algorithms and the output of these functions is the local models
   that are send around. Input is therefore normally the csv data.
   :ref:`You can read more here <sens anchor>`

   There are two ways to find the correct sensitivity.

   #. For many functions, e.g. for any count query, the sensitivity is fixed
      and can be found with some research.

   #. Alternatively, the so called local sensitivity can be calculated:
      :math:`max_{D, D'} ||function(D) - function(D')||p`
      Where `D` is all data, `D'` is all data except for one row and `p` is 1
      for laplace noise and 2 for gauss noise.
      In practice, that means generating the model using all data except for one
      row, for EACH row, and then finding the norm of the biggest pairwise
      difference of these models. This method is computationally intense, it
      transforms any training algorithm of O(1) into O(N*1), where N is the
      databasesize. :ref:`See this section for more information about this
      method and what the sensitivty is <sens anchor>`

   In case both of these ways are not feasible or in case clipping the values is
   beneficial, the **clippingVal** can be used. The right value for **clippingVal**
   depends largely on the data and the training algorithm, but generally it
   should be choosen as low as possible without the scaling down of values
   interfering with training. To understand what **clipping** does, see
   :ref:`here <clipping anchor>`

.. _delta anchor:

2. **delta**:
   When using laplace noise, **delta** must be 0. When using gauss noise, **delta**
   must be smaller than 1.
   We recomment setting **delta** to a smaller scale than the value
   :math:`\frac{1}{numberRows}` as proposed by
   `[Dwork et al 2014] <http://dx.doi.org/10.1561/0400000042>`_.

.. _eps anchor:

3. **epsilon**:
   For choosing epsilon, we recommend choosing of the following 3 tiers as
   proposed by `[Ponomareva et al, 2023] <https://doi.org/10.1613/jair.1.14649>`_.
   Generally, the lowest possible epsilon should be choosen.
   Either different epsilons can be tested locally or the 3 tiers can be
   iterated from most strict (1) to most loose(3) until a satisfactory result
   is reached.

  * **Tier 1: Strong formal privacy guarantees**: **epsilon < 1**

    This gives formal guarantees and high protection, but often heavily
    decreases accuracy.

  * **Tier 2: Reasonable privacy guarantees**: **epsilon <= 10**

    This tier is currently the most used. It gives reasonable protection but
    can still produce acceptable results. Technically DP with gauss noise is not
    defined for any epsilon > 1, while in practice the
    protection is still reasonable.

  * **Tier 3**: **epsilon ~ few 100s**

    While formally, this tier offers no protection, in practice, data
    reconstruction attacks can still be prevented using an epsilon of a
    few 100s, e.g. upto 300, see e.g. `[Balle et al, 2022] <https://doi.org/10.1109/SP46214.2022.9833677>`_.





Background
^^^^^^^^^^

.. _sens anchor:

Sensitivity
"""""""""""
Sensitivity is a metric to reveal the privacy loss through publishing of the
result of some function, in our case publishing of the model of a training
algorithm.
There are two forms of sensitivity:

1. Global Sensitivity:
   :math:`\Delta f = \max_{D}{||f(D) - f(D')||p}`

2. Local Sensitivity:
   :math:`\Delta f = \max_{D, D'}{||f(D) - f(D')||p}`

Global sensitivity considers *ANY* data used, while local sensitivity considers
some specific data. :math:`D'` considers all of :math:`D` except for one row.
Local sensitivty tends to be lower and therefore needs less noising, but is
also more computationally intense to calculate.
The method of finding the local sensitivity is the following::

   Input:
     Data D:      A collection of rows, where each row represents only ONE
                  individual, e.g. any csv data WITHOUT repeating ids.
     Function f:  The training algorithm that gets used and whose output is sent
     Norm p:      The norm to be used for the sensitivity. p = 1 is used for
                  laplace noise and delivers the L1-Sensitivity, p = 2 is used
                  for gaussian noise and delivers the L2-Sensitivity
   Output:
     Sensitivity: The L1/L2-Sensitivity of F considering D. L1 or L2 is decided
                  depending on given norm p
   Algorithm:
     sensitivity = 0
     basemodel = f(D)
     for row in data:
       D_prime = D.remove(row)
         # remove returns a copy of D without row while not changing D
       sensitivity = max(sensitivity, ||basemodel - f(D_prime)||p)
     return sensitivity


.. _clipping anchor:

Clipping
""""""""
The **clippingVal** defines the maximum p-norm of the numerical data that is send
with DP. For laplace noise, the 1-norm is used, for gauss noise the 2-norm. This
comes from the fact that laplace uses L1-Sensitivity, while gauss noise uses
L2-Sensitivity.
If the norm exceeds the **clippingVal**, then the values are scaled down.
The scalling happens according to the following formula:

:math:`w_{clipped} = w \cdot \min{(1, \frac{C}{||w||p})}`, where
:math:`w` is the numerical data which gets clipped and C is the clippingVal.

Given clipping, the sensitivity is fixed as :math:`2 \cdot C`.
This is due to the fact that when using clipping, :math:`w` can
at most change from being the biggest postive norm value to the smallest
negative norm value.