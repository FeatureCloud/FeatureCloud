"""
Test module documentation string for app.py
"""
import abc
import datetime
import json
import numpy as np
import pickle
import sys
import threading
import traceback

from enum import Enum
from time import sleep
from typing import Dict, List, Tuple, Union, TypedDict, Literal

DATA_POLL_INTERVAL = 0.1  # Interval (seconds) to check for new data pieces, adapt if necessary
TERMINAL_WAIT = 10  # Time (seconds) to wait before final shutdown, to allow the controller to pick up the newest
# progress etc.
TRANSITION_WAIT = 1  # Time (seconds) to wait between state transitions


class Role(Enum):
    """
    | Describes the Role of a client
    | Can be one of the following values:
    | Role.PARTICIPANT
    | Role.COORDINATOR
    | Role.BOTH
    """
    PARTICIPANT = (True, False)
    COORDINATOR = (False, True)
    BOTH = (True, True)


class State(Enum):
    """
    | Describes the current State of the app instance
    | Can be one of the following values:
    | State.RUNNING
    | State.ERROR
    | State.ACTION
    """
    RUNNING = 'running'
    ERROR = 'error'
    ACTION = 'action_required'


class SMPCOperation(Enum):
    """
    | It's parameters are used to describe SMPC Operations for other functions
    | One of the following:
    | SMPCOperation.ADD
    | SMPCOperation.MULTIPLY
    """
    ADD = 'add'
    MULTIPLY = 'multiply'


class SMPCSerialization(Enum):
    """
    | Describes the serialization used with data when using SMPC, so the format data is send between different components of Featurecloud, e.g. between the app instance and the controller
    | Currently ony the following is supported
    | SMPCSerialization.JSON
    """
    JSON = 'json'


class LogLevel(Enum):
    """
    | The level of a log, given to the log function.
    | LogLevel.DEBUG: Just for debugging
    | LogLevel.ERROR: Throws an error but does not halt the program
    | LogLevel.FATAL: Stops the program
    """
    DEBUG = 'info'
    ERROR = 'error'
    FATAL = 'fatal'

class DPNoisetype(Enum):
    GAUSS = 'gauss'
    LAPLACE = 'laplace'

class DPSerialization(Enum):
    JSON = 'json'


class SMPCType(TypedDict):
    operation: Literal['add', 'multiply']
    serialization: Literal['json']
    shards: int
    exponent: int

class DPType(TypedDict):
    serialization: Literal['json']
    noisetype: Literal['gauss', 'laplace']
    epsilon: float
    delta: float
    sensitivity: Union[float, None]
    clippingVal: Union[float, None]

class App:
    """ Implementing the workflow for the FeatureCloud platform.

    Attributes
    ----------
    id: str
    coordinator: bool
    clients: list

    status_available: bool
    status_finished: bool
    status_message: str
    status_progress: float
    status_state: str
    status_destination: str
    status_smpc: dict

    default_smpc: dict
    default_dp: dict

    data_incoming: list
    data_outgoing: list
    thread: threading.Thread

    states: Dict[str, AppState]
    transitions: Dict[str, Tuple[AppState, AppState, bool, bool]]
    transition_log: List[Tuple[datetime.datetime, str]]
    internal: dict

    current_state: str


    Methods
    -------
    handle_setup(client_id, coordinator, clients)
    handle_incoming(data)
    handle_outgoing()
    guarded_run()
    run()
    register()
    _register_state(name, state, participant, coordinator, **kwargs)
    register_transition(name, source, participant, coordinator)
    transition()
    log()
    """

    def __init__(self):
        self.id = None
        self.coordinator = None
        self.clients = None

        self.thread: Union[threading.Thread, None] = None

        self.status_available: bool = False
        self.status_finished: bool = False
        self.status_message: Union[str, None] = None
        self.status_progress: Union[float, None] = None
        self.status_state: Union[str, None] = None
        self.status_destination: Union[str, None] = None
        self.status_smpc: Union[SMPCType, None] = None
        self.status_dp: Union[DPType, None] = None

        self.data_incoming = []
        self.data_outgoing = [] # list of lists[data, use_smpc_bool, use_dp_bool, destination]
                                # destination of None sends the data to the coordinator

        self.default_smpc: SMPCType = {'operation': 'add', 'serialization': 'json', 'shards': 0, 'exponent': 8}
        self.default_dp: DPType = {'serialization': 'json', 'noisetype': 'laplace',
                                   'epsilon': 1.0, 'delta': 0.0,
                                   'sensitivity': None, 'clippingVal': 10.0}

        self.current_state: Union[AppState, None] = None
        self.states: Dict[str, AppState] = {}
        #self.transitions: Dict[
        #    str, Tuple[AppState, AppState, bool, bool]] = {}  # name => (source, target, participant, coordinator)
        self.transitions: Dict[
            str, Tuple[AppState, AppState, bool, bool, str]] = {}  # name => (source, target, participant, coordinator, label)

        self.transition_log: List[Tuple[datetime.datetime, str]] = []

        self.internal = {}

        # Add terminal state
        @app_state('terminal', Role.BOTH, self)
        class TerminalState(AppState):
            def register(self):
                pass

            def run(self) -> str:
                pass

    def handle_setup(self, client_id, coordinator, clients):
        """ It will be called on startup and contains information about the
            execution context of this instance. And registers all of the states.


        Parameters
        ----------
        client_id: str
        coordinator: bool
        clients: list

        """
        self.id = client_id
        self.coordinator = coordinator
        self.clients = clients

        self.log(f'id: {self.id}')
        self.log(f'coordinator: {self.coordinator}')
        self.log(f'clients: {self.clients}')

        self.current_state = self.states.get('initial')

        if not self.current_state:
            self.log('initial state not found', level=LogLevel.FATAL)

        self.thread = threading.Thread(target=self.guarded_run)
        self.thread.start()

    def guarded_run(self):
        """ run the workflow while trying to catch possible exceptions

        """
        try:
            self.run()
        except Exception as e:  # catch all  # noqa
            self.log(traceback.format_exc())
            self.status_message = e.__class__.__name__
            self.status_state = State.ERROR.value
            self.status_finished = True

    def run(self):
        """    Runs the workflow, logs the current state, executes it,
               and handles the transition to the next desired state.
               Once the app transits to the terminal state, the workflow will be terminated.

       """
        while True:
            self.log(f'state: {self.current_state.name}')
            transition = self.current_state.run()
            self.log(f'transition: {transition}')
            self.transition(f'{self.current_state.name}_{transition}')
            if self.current_state.name == 'terminal':
                self.status_progress = 1.0
                self.log('done')
                sleep(TERMINAL_WAIT)
                self.status_finished = True
                return
            sleep(TRANSITION_WAIT)

    def register(self):
        """ Registers all of the states transitions
            it should be called once all of the states are registered.

        """
        for s in self.states:
            state = self.states[s]
            state.register()

    def handle_incoming(self, data, client):
        """ When new data arrives, it appends it to the
            `data_incoming` attribute to be accessible for app states.

        Parameters
        ----------
        data: list
            encoded data
        client: str
            Id of the client that Sent the data

        """
        self.data_incoming.append((data, client))

    def handle_outgoing(self):
        """ When it is requested to send some data to other client/s
            it will be called to deliver the data to the FeatureCloud Controller.
            Then sets status variables (status_*) accordingly for the next data to send from
            self.data_outgoing

        """
        if len(self.data_outgoing) == 0:
            return None
        data = self.data_outgoing[0]
        self.data_outgoing = self.data_outgoing[1:] # use data_outgoing as queue, sending one data
                                                    # piece at a time
        if len(self.data_outgoing) == 0:
            self.status_available = False
            self.status_destination = None
            self.status_smpc = None
            self.status_dp = None
        else:
            self.status_available = True
            self.status_smpc = self.default_smpc if self.data_outgoing[0][1] else None
            self.status_dp = self.default_dp if self.data_outgoing[0][2] else None
            self.status_destination = self.data_outgoing[0][3]
        return data[0]

    def _register_state(self, name, state, participant, coordinator, **kwargs):
        """ Instantiates a state, provides app-level information and adds it as part of the app workflow.

        Parameters
        ----------
        name: str
        state: AppState
        participant: bool
        coordinator: bool

        """
        if self.transitions.get(name):
            self.log(f'state {name} already exists', level=LogLevel.FATAL)

        si = state(**kwargs)
        si._app = self
        si.name = name
        si.participant = participant
        si.coordinator = coordinator
        self.states[si.name] = si

    def register_transition(self, name: str, source: str, target: str, participant=True, coordinator=True, label: Union[str,None] = None):
        """ Receives transition registration parameters, check the validity of its logic,
            and consider it as one possible transitions in the workflow.
            There will be exceptions if apps try to register a transition with contradicting roles.

        Parameters
        ----------
        name: str
            Name of the transition
        source: str
            Name of the source state
        target: str
            Name of the target state
        participant: bool
            Indicates whether the transition is allowed for participant role
        coordinator: bool
            Indicates whether the transition is allowed for the coordinator role

        """
        if not participant and not coordinator:
            self.log('either participant or coordinator must be True', level=LogLevel.FATAL)

        if self.transitions.get(name):
            self.log(f'transition {name} already exists', level=LogLevel.FATAL)

        source_state = self.states.get(source)
        if not source_state:
            self.log(f'source state {source} not found', level=LogLevel.FATAL)
        if participant and not source_state.participant:
            self.log(f'source state {source} not accessible for participants', level=LogLevel.FATAL)
        if coordinator and not source_state.coordinator:
            self.log(f'source state {source} not accessible for the coordinator', level=LogLevel.FATAL)

        target_state = self.states.get(target)
        if not target_state:
            self.log(f'target state {target} not found', level=LogLevel.FATAL)
        if participant and not target_state.participant:
            self.log(f'target state {target} not accessible for participants', level=LogLevel.FATAL)
        if coordinator and not target_state.coordinator:
            self.log(f'target state {target} not accessible for the coordinator', level=LogLevel.FATAL)

        self.transitions[name] = (source_state, target_state, participant, coordinator, label)

    def transition(self, name):
        """ Transits the app workflow to the unique next state based on
            current states, the role of the FeatureCloud client,
            and requirements of registered transitions for the current state.

        Parameters
        ----------
        name: str
            Name of the transition(which includes name of current and the next state).

        """
        transition = self.transitions.get(name)
        if not transition:
            self.log(f'transition {name} not found', level=LogLevel.FATAL)
        if transition[0] != self.current_state:
            self.log('current state unequal to source state', level=LogLevel.FATAL)
        if not transition[2] and not self.coordinator:
            self.log(f'cannot perform transition {name} as participant', level=LogLevel.FATAL)
        if not transition[3] and self.coordinator:
            self.log(f'cannot perform transition {name} as coordinator', level=LogLevel.FATAL)

        self.transition_log.append((datetime.datetime.now(), name))
        self.current_state = transition[1]

    def log(self, msg, level: LogLevel = LogLevel.DEBUG):
        """
        Prints a log message or raises an exception according to the log level.

        Parameters
        ----------
        msg : str
            message to be displayed
        level : LogLevel, default=LogLevel.DEBUG
            determines the channel (stdout, stderr) or whether to trigger an exception
        """

        msg = f'[Time: {datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")}] [Level: {level.value}] {msg}'

        if level == LogLevel.FATAL:
            raise RuntimeError(msg)
        if level == LogLevel.ERROR:
            print(msg, flush=True, file=sys.stderr)
        else:
            print(msg, flush=True)

class AppState(abc.ABC):
    """ Defining custom states

    AppState is the class used when programming a FeatureCloud App to create
    states and to communicate with other clients. Generally, a FeatureCloud app
    consists of different states that all share the same AppState class.
    The states themselves are created as classes with the
    @app_state("statename") decorator.
    See the example below or the template apps for more details.

    Examples
    --------
    ::

        # A simple example for a typical federated learning app
        from FeatureCloud.app.engine.app import AppState, app_state, Role, LogLevel

        # an intial state for loading the data
        @app_state("initial")
        class InitialState(AppState): # you can choose any fitting classname
          def register(self):
            self.register_transition("local_computation", Role.BOTH)
              # Role.BOTH means that this transition can be done by
              # the coordinator and a participant
          def run(self):
            # Here you can for example load the config file and the data
            dataFile = os.path.join(os.getcwd(), "mnt", "input", "data.csv"))
            data = pd.read_csv(dataFile)
            # Data can be stored for access in other states like this
            self.store(key = "keyData", value=data)
            # Also store some intial model
            self.store(key = "model", value=np.zeros(5))
            # to progress to another state, simply return the states name
            return "local_computation"

        # a state for the local computation
        @app_state
        class local_computation(AppState):
          def register(self):
            self.register_transition("aggregate_data", Role.COORDINATOR)
            self.register_transition("obtain_weights", Role.PARTICIPANT)

          def run(self):
            # do some local computations
            model = calculateThings(self.load("keyData"), self.load("model"))
              # loads the data and calculates some model
            self.send_data_to_coordinator(model,
                                        send_to_self=True,
                                        use_smpc=False)
            if self.is_coordinator:
              return "aggregate"
            else:
              return "obtain_weights"

        # a state just for obtaining the weights from the coordinator
        @app_state("obtain_weights")
        class obtainWeights(AppState):
          def register(self):
            self.register_transition("local_computation", Role.BOTH)

          def run(self):
            updated_model = self.await_data(n = 1,)
              # n=1 since we only expect one model from the coordinator
            self.store("model", updated_model)
            return "local_computation"

        # a state for the coordinator to aggregate all weights
        @app_state("aggregate_data")
        class aggregateDataState(AppState):
          def register(self):
            self.register_transition("obtain_weights", Role.COORDINATOR)
            self.register_transition("terminal", Role.COORDINATOR)
          def run(self):
            aggregated_model = self.aggregate_data(operation = SMPCOperation.ADD)
              # waits for every participant to send someting and then
              # adds them together
            updated_model = aggregated_model / len(self.clients)
            if stop_training_criteria: # if the training is done
              fp = open(os.path.join("mnt", "output", "trained_model.pyc"), "wb")
              np.save(fp, updated_model)
              return "terminal"
                # going to the terminal state will finnish the app and tell
                # all clients that the computation is done
            else:
              self.broadcast_data(updated_model, send_to_self = True)
              return "obtain_weights"

    Attributes
    ----------
    app: App
    name: str
    participant: bool
    coordinator: bool

    Methods
    -------
    register()
    run()
    register_transition(target, role, name)
    aggregate_data(operation, use_smpc)
    gather_data(is_json)
    await_data(n, unwrap, is_json)
    send_data_to_participant(data, destination)
    configure_smpc(exponent, shards, operation, serialization)
    send_data_to_coordinator(data, send_to_self, use_smpc)
    broadcast_data(data, send_to_self)
    update(message, progress, state)

    """

    def __init__(self):
        self._app = None
        self.name = None
        self.participant = None
        self.coordinator = None

    @abc.abstractmethod
    def register(self):
        """ This is an abstract method that should be implemented by developers
            it calls AppState.register_transition to register transitions for state.
            it will be called in App.register method so that, once all states are defined,
            in a verifiable way, all app transitions can be registered.

        """

    @abc.abstractmethod
    def run(self) -> str:
        """ It is an abstract method that should be implemented by developers,
            to execute all local or global operation and calculations of the state.
            It will be called in App.run() method so that the state perform its operations.

        """

    @property
    def is_coordinator(self):
        return self._app.coordinator

    @property
    def clients(self):
        return self._app.clients

    @property
    def id(self):
        return self._app.id

    def register_transition(self, target: str, role: Role = Role.BOTH, name: Union[str, None] = None, label: Union[str, None] = None):
        """
        Registers a transition in the state machine.

        Parameters
        ----------
        target : str
            name of the target state
        role : Role, default=Role.BOTH
           role for which this transition is valid
        name : str or None, default=None
            name of the transition
        """

        if not name:
            name = target
        participant, coordinator = role.value
        self._app.register_transition(f'{self.name}_{name}', self.name, target, participant, coordinator, label)

    def aggregate_data(self, operation: SMPCOperation = SMPCOperation.ADD, use_smpc=False,
                       use_dp=False):
        """
        Waits for all participants (including the coordinator instance) to send data and returns the aggregated value.

        Parameters
        ----------
        operation : SMPCOperation
            specifies the aggregation type
        use_smpc : bool, default=False
            if True, the data to be aggregated is expected to stem from an SMPC aggregation
        use_dp: bool, default=False
            if True, clients sent their data adding dp via the use_dp option in the send functions
            this means the data is in json format

        Returns
        -------
        aggregated value
        """

        if use_smpc:
            return self.await_data(1, unwrap=True, is_json=True)  # Data is aggregated already
        elif use_dp:
            data = self.gather_data(is_json=True)
            return _aggregate(data, operation)
        else:
            data = self.gather_data(is_json=False)
            return _aggregate(data, operation)  # Data needs to be aggregated according to operation

    def gather_data(self, is_json=False, use_smpc=False, use_dp=False):
        """
        Waits for all participants (including the coordinator instance) to send data and returns a list containing the received data pieces. Only valid for the coordinator instance.

        Parameters
        ----------
        use_smpc: bool, default=False
            Indicated whether the data that is gather was sent using SMPC.
            If this is not set to True when data was sent using SMPC, this 
            function ends up in an endless loop
        use_dp: bool, default=False
        is_json : bool, default=False
            [deprecated] when data was sent via DP or SMPC, the data is sent in
            JSON serialization. This was used to indicate this but is now 
            DEPRICATED, use use_smpc/use_dp accordingly instead, they will take
            care of serialization automatically.
        Returns
        -------
        list of n data pieces, where n is the number of participants
        """
        if not self._app.coordinator:
            self._app.log('must be coordinator to use gather_data', level=LogLevel.FATAL)
        n = len(self._app.clients)
        if use_smpc or use_dp:
            is_json = True
        if use_smpc:
            n = 1
        return self.await_data(n, unwrap=False, is_json=is_json)

    def await_data(self, n: int = 1, unwrap=True, is_json=False):
        """
        Waits for n data pieces and returns them.

        Parameters
        ----------
        n : int, default=1
            number of data pieces to wait for
        unwrap : bool, default=True
            if True, will return the first element of the collected data (only useful if n = 1)
        is_json : bool, default=False
            if True, expects JSON serialized values and deserializes it accordingly
            JSON serialization is used with SMPC and DP, so when SMPC or DP was used
            in the corresponding send_data, is_json should be true.
            Data sent via broadcast however is always serialized via pickle, so for
            if the await_data expects data from broadcast, is_json=False should be used

        Returns
        -------
        list of data pieces (if n > 1 or unwrap = False) or a single data piece (if n = 1 and unwrap = True)
        """
        while True:
            if len(self._app.data_incoming) >= n:
                data = self._app.data_incoming[:n]
                self._app.data_incoming = self._app.data_incoming[n:]
                if n == 1 and unwrap:
                    return _deserialize_incoming(data[0][0], is_json=is_json)
                else:
                    return [_deserialize_incoming(d[0], is_json=is_json) for d in data]

            sleep(DATA_POLL_INTERVAL)

    def send_data_to_participant(self, data, destination, use_dp=False):
        """
        Sends data to a particular participant identified by its ID.

        Parameters
        ----------
        data : object
            data to be sent
        destination : str
            destination client ID
        """

        data = _serialize_outgoing(data, is_json=use_dp)
        if destination == self._app.id and not use_dp:
            # In no DP case, the data does not have to be sent via the controller
            self._app.data_incoming.append((data, self._app.id))
        else:
            self._app.data_outgoing.append((data, False, use_dp, destination))
            self._app.status_destination = destination
            self._app.status_smpc = None
            self._app.status_dp = self._app.default_dp if use_dp else None
            self._app.status_available = True

    def send_data_to_coordinator(self, data, send_to_self=True, use_smpc=False,
                                 use_dp=False):
        """
        Sends data to the coordinator instance.

        Parameters
        ----------
        data : object
            data to be sent
        send_to_self : bool, default=True
            if True, the data will also be sent internally to this instance (only applies to the coordinator instance)
        use_smpc : bool, default=False
            if True, the data will be sent as part of an SMPC aggregation step
        use_dp : bool, default=False
            if True, the data will be noised before sending according to the
            saved dp configuration
        """
        if use_smpc or use_dp:
            data = _serialize_outgoing(data, is_json=True)

        else:
            data = _serialize_outgoing(data, is_json=False)

        if self._app.coordinator and not use_smpc and not use_dp:
            # coordinator sending itself data, if that is wanted (send_to_self),
            # and neither dp nor smpc are used, the controller does not have to be used
            # for sending the data
            if send_to_self:
                self._app.data_incoming.append((data, self._app.id))
        else:
            # for SMPC and DP, the data has to be sent via the controller
            self._app.data_outgoing.append((data, use_smpc, use_dp, None))
            if use_dp and self._app.coordinator:
                # give the coordinator as destination,
                # else, it will be interpreted as a broadcast action
                self._app.status_destination = self._app.id
            else:
                self._app.status_destination = None
            self._app.status_smpc = self._app.default_smpc if use_smpc else None
            self._app.status_dp = self._app.default_dp if use_dp else None
            self._app.status_available = True

    def broadcast_data(self, data, send_to_self=True, use_dp = False):
        """
        Broadcasts data to all participants (only valid for the coordinator instance).

        Parameters
        ----------
        data : object
            data to be sent
        send_to_self : bool
            if True, the data will also be sent internally to this coordinator instance
        use_dp : bool
            if True, data will be noised with DP before being broadcasted
        """
        if not self._app.coordinator:
            self._app.log('only the coordinator can broadcast data', level=LogLevel.FATAL)

        if use_dp:
            self.send_data_to_participant(data,
                                          destination=self.id,
                                          use_dp=True)
            data = self.await_data(n = 1,
                                   unwrap=True,
                                   is_json=True)

        # serialize before broadcast
        data = _serialize_outgoing(data, is_json=False)

        self._app.data_outgoing.append((data, False, False, None))
        self._app.status_destination = None
        self._app.status_smpc = None
        self._app.status_dp = None
        self._app.status_available = True
        if send_to_self:
            self._app.data_incoming.append((data, self._app.id))

    def configure_smpc(self, exponent: int = 8, shards: int = 0, operation: SMPCOperation = SMPCOperation.ADD,
                       serialization: SMPCSerialization = SMPCSerialization.JSON):
        """
        Configures successive usage of SMPC aggregation performed in the FeatureCloud controller.

        Parameters
        ----------
        exponent : int, default=8
            exponent to be used for converting floating point numbers to fixed-point numbers
        shards : int, default=0
            number of secrets to be created, if 0, the total number of participants will be used
        operation : SMPCOperation, default=SMPCOperation.ADD
            operation to perform for aggregation
        serialization : SMPCSerialization, default=SMPCSerialization.JSON
            serialization to be used for the data
        """

        self._app.default_smpc['exponent'] = exponent
        self._app.default_smpc['shards'] = shards
        self._app.default_smpc['operation'] = operation.value
        self._app.default_smpc['serialization'] = serialization.value

    def configure_dp(self, epsilon: float = 1.0, delta: float =  0.0,
                     sensitivity: float or None = None,
                     clippingVal: float or None = 10.0,
                     noisetype: DPNoisetype = DPNoisetype.LAPLACE):
        """
        Configures the usage of differential privacy inside the FeatureCloud
        controller

        Parameters
        ----------
        epsilon: : float, default = 1.0
            the epsilon value determining how much privacy is wanted
        delta : float, default = 0.0
            the delta value determining how much privacy is wanted. Should be 0
            when using laplace noise (noisetype=DPNoisetype.LAPLACE)
        clippingVal : float, 10.0
            Determines the scaling down of values sent via the controller.
            if e.g. an array of 5 numeric values ( 5 weights) is sent via the
            controller and clippingVal = 10.0 is choosen, then the p-norm of all
            5 values will not exceed 10. For laplace the 1-norm is choosen, for
            gauss noise the 2-norm.
        noisetype: DPNoisetype.LAPLACE or DPNoisetype.GAUSS, default = DPNoisetype.LAPLACE
            The distribution of noise added when adding differential privacy to
            the model
        """
        if sensitivity and sensitivity == 0:
            self._app.log('DP was configured to a sensitivity of 0, therefore '+\
                          'deactivating DP. Use sensitivity = None if sensitivity '+\
                          'given via clipping should be used',  level=LogLevel.FATAL)
        if clippingVal and clippingVal == 0:
            self._app.log('DP was configured to a clippingVal of 0, this would '+\
                          'block all learning. Use clippingVal = None if '+\
                          'no clipping of models is wanted. In that case, ' +\
                          'a sensitivity value is needed to use DP',  level=LogLevel.FATAL)
        if not delta:
            self._app.log("Delta not given, please give a delta value or DP cannot be applied",
                          level=LogLevel.FATAL)
        if not epsilon:
            self._app.log("Epsilon not given, please give an epsilon value or DP cannot be applied",
                          level=LogLevel.FATAL)
        if not noisetype:
            self._app.log("noisetype not given, please give an noisetype value or DP cannot be applied",
                          level=LogLevel.FATAL)
        if epsilon <= 0:
            self._app.log("invalid epsilon given, epsilon must be a positive number",
                          level=LogLevel.FATAL)
        if delta <= 0:
            self._app.log("invalid delta given, delta must be >= 0",
                          level=LogLevel.FATAL)
        if noisetype == DPNoisetype.LAPLACE and delta != 0:
            self._app.log("When using laplace noise, delta must be set to 0!",
                          level=LogLevel.FATAL)
        if noisetype == DPNoisetype.GAUSS:
            if delta <= 0:
                self._app.log("When using gauss noise, delta must be >= 0",
                          level=LogLevel.FATAL)
            if epsilon >= 1:
                self._app.log("When using gauss noise, epsilon must be 0 < eps < 1",
                          level=LogLevel.FATAL)

        self._app.default_dp['serialization'] = 'json'
        self._app.default_dp['noisetype'] = noisetype.value
        self._app.default_dp['epsilon'] = epsilon
        self._app.default_dp['delta'] = delta
        self._app.default_dp['sensitivity'] = sensitivity
        self._app.default_dp['clippingVal'] = clippingVal



    def update(self, message: Union[str, None] = None, progress: Union[float, None] = None,
               state: Union[State, None] = None):
        """
        Updates information about the execution.

        Parameters
        ----------
        message : str
            message briefly summarizing what is happening currently
        progress : float
            number between 0 and 1, indicating the overall progress
        state : State or None
            overall state (running, error or action_required)
        """

        if message and len(message) > 40:
            self._app.log('message is too long (max: 40)', level=LogLevel.FATAL)
        if progress is not None and (progress < 0 or progress > 1):
            self._app.log('progress must be between 0 and 1', level=LogLevel.FATAL)
        if state is not None and state != State.RUNNING and state != State.ERROR and state != State.ACTION:
            self._app.log('invalid state', level=LogLevel.FATAL)
        self._app.status_message = message
        self._app.status_progress = progress
        self._app.status_state = state.value if state else None

    def store(self, key: str, value):
        """ Store allows to share data across different AppState instances.

        Parameters
        ----------
        key: str
        value:

        """
        self._app.internal[key] = value

    def load(self, key: str):
        """ Load allows to access data shared across different AppState instances.

        Parameters
        ----------
        key: str

        Returns
        -------
        value:
            Value stored previously using store

        """
        return self._app.internal.get(key)

    def log(self, msg, level: LogLevel = LogLevel.DEBUG):
        """
        Prints a log message or raises an exception according to the log level.

        Parameters
        ----------
        msg : str
            message to be displayed
        level : LogLevel, default=LogLevel.DEBUG
            determines the channel (stdout, stderr) or whether to trigger an exception
        """

        self._app.log(f'[State: {self.name}] {msg}', level)


def app_state(name: str, role: Role = Role.BOTH, app_instance: Union[App, None] = None, **kwargs):
    if app_instance is None:
        app_instance = app

    participant, coordinator = role.value
    if not participant and not coordinator:
        app_instance.log('either participant or coordinator must be True', level=LogLevel.FATAL)

    def func(state_class):
        app_instance._register_state(name, state_class, participant, coordinator, **kwargs)
        return state_class

    return func

class _NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            # call default Encoder in other cases
            return json.JSONEncoder.default(self, obj)

def _serialize_outgoing(data, is_json=False):
    """
    Transforms a Python data object into a byte serialization.

    Parameters
    ----------
    data : object
        data to serialize
    is_json : bool, default=False
        indicates whether JSON serialization is required

    Returns
    ----------
    serialized data as bytes
    """

    if not is_json:
        return pickle.dumps(data)

    # we use a custom cls to manage numpy which is quite common
    return json.dumps(data, cls=_NumpyArrayEncoder)


def _deserialize_incoming(data: bytes, is_json=False):
    """
    Transforms serialized data bytes into a Python object.

    Parameters
    ----------
    data : bytes
        data to deserialize
    is_json : bool, default=False
        indicates whether JSON deserialization should be used

    Returns
    ----------
    deserialized data
    """
    if not is_json:
        return pickle.loads(data)

    return json.loads(data)


def _aggregate(data, operation: SMPCOperation):
    """
    Aggregates a list of received values.

    Parameters
    ----------
    data : array_like
        list of data pieces
    operation : SMPCOperation
        operation to use for aggregation (add or multiply)

    Returns
    ----------
    aggregated value
    """
    data_np = [np.array(d) for d in data]

    aggregate = data_np[0]

    if operation == SMPCOperation.ADD:
        for d in data_np[1:]:
            aggregate = aggregate + d

    if operation == SMPCOperation.MULTIPLY:
        for d in data_np[1:]:
            aggregate = aggregate * d

    return aggregate


app = App()
