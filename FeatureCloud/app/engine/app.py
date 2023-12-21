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
    send_counter: int
    receive_counter: int
    status_available: bool 
    status_finished: bool
    status_message: str
    status_progress: float
    status_state: str
    status_destination: str
    status_smpc: SMPCType
    status_dp: DPType
    status_memo: str

    default_smpc: dict
    default_dp: dict

    data_incoming: dict[str]: [(data, sendingClientID: str),...]
    data_outgoing: list[(data, statusJSON: str)]
    thread: threading.Thread

    states: Dict[str, AppState]
    transitions: Dict[str, Tuple[AppState, AppState, bool, bool]]
    transition_log: List[Tuple[datetime.datetime, str]]
    internal: dict

    current_state: AppState
    last_send_status: str (JSON)

    Methods
    -------
    handle_setup(client_id, coordinator, clients)
    handle_incoming(data)
    handle_outgoing()
    get_current_status(**kwargs)
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
        self.coordinatorID = None
        self.clients = None
        self.default_memo = None
        self.thread: Union[threading.Thread, None] = None
        self.send_counter: int = 0 
        self.receive_counter: int = 0
            # the send counter is increased with any send_data_to_coordinator
            # call while the receive counter is increased with any
            # aggregate_data and gather_data call as well as with
            # await_data with n=#clients OR n=#clients-1 OR n=1 and smpc=True
            # This should work in 99% of all cases, except when
            # somebody uses send_data_to_participant from each client and then
            # uses await_data on all these #clients -1 data pieces.
        self.data_incoming = {}
            # dictionary mapping memo: [(data, client),...]
            # data is the data serialized with JSON when SMPC or DP is used, 
            # otherwise serialized the way that the sender used (usually pickle)
            # client is the id of the client that sent the data
            # memo is the memo send alongside the data to identify to which
            # comunication round the data belongs to
        self.data_outgoing = [] 
            # list of all data objects and the corresponding status to use with them
            # format: list of tuples, each tuple contains dataObject, status as JSON string

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

        self.status_available: bool = False
        self.status_finished: bool = False
        self.status_message: Union[str, None] = None
        self.status_progress: Union[float, None] = None
        self.status_state: Union[str, None] = None
        self.status_destination: Union[str, None] = None
        self.status_smpc: Union[SMPCType, None] = None
        self.status_dp: Union[DPType, None] = None
        self.status_memo: Union[str, None] = None

        self.last_send_status = self.get_current_status()
        
        # Add terminal state
        @app_state('terminal', Role.BOTH, self)
        class TerminalState(AppState):
            def register(self):
                pass

            def run(self) -> Union[str, None]:
                pass

    def handle_setup(self, client_id, coordinator, clients, coordinatorID=None):
        """ It will be called on startup and contains information about the
            execution context of this instance. And registers all of the states.


        Parameters
        ----------
        client_id: str
        coordinator: bool
        clients: list
        coordinatorID: str

        """
        self.id = client_id
        self.coordinator = coordinator
        self.coordinatorID = coordinatorID
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
            self.data_outgoing.insert(0, (None, self.get_current_status(
                finished=True, state=State.ERROR.value, 
                message=e.__class__.__name__)))
              # remove ANY data in the pipeline and crash the workflow 
              # on the next poll

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
                sleep(TERMINAL_WAIT) 
                terminal_status_added = False
                while True:
                    if not terminal_status_added:
                        # add finished status answer to the outgoing data queue
                        status = self.get_current_status(progress=1.0, 
                                                         message="terminal", 
                                                         finished=True)
                        self.data_outgoing.append((None, status)) 
                            # only append to ensure that all data in the pipe is still
                            # sent out
                        terminal_status_added = True
                        sleep(TERMINAL_WAIT) 
                            # potentially this wait time clears the queue already
                    if len(self.data_outgoing) > 1:
                        # there is still data to be sent out
                        self.log(f'done, waiting for the last {len(self.data_outgoing)-1} data pieces to be send')
                    elif len(self.data_outgoing) == 1:
                        sleep(TERMINAL_WAIT) 
                            # the last status that was added before is never
                            # removed, so we finnish when only one status is 
                            # left
                            # To ensure that this last status has been pulled,
                            # we just wait 
                        self.log('done')
                        return 
                    sleep(TRANSITION_WAIT)
            sleep(TRANSITION_WAIT)

    def register(self):
        """ Registers all of the states transitions
            it should be called once all of the states are registered.

        """
        for s in self.states:
            state = self.states[s]
            state.register()

    def get_current_status(self, **kwargs):
        status = dict()
        status["available"] = self.status_available
        status["finished"] = self.status_finished
        status["message"] = self.status_message
        status["progress"] = self.status_progress
        status["state"] = self.status_state
        status["destination"] = self.status_destination
        status["smpc"] = self.status_smpc
        status["dp"] = self.status_dp
        status["memo"] = self.status_memo
        for key, value in kwargs.items():
            # set whatever is wanted from the arguments
            status[key] = value
        return status
    
    def handle_incoming(self, data, client, memo=None):
        """ When new data arrives, it appends it to the
            `data_incoming` attribute to be accessible for app states.

        Parameters
        ----------
        data: list
            encoded data
        client: str
            Id of the client that Sent the data

        """
        if memo not in self.data_incoming:
            self.data_incoming[memo] = [(data, client)]
        else:
            self.data_incoming[memo].append((data, client))

    def handle_status(self):
        """ This informs if there is any data to be sent as well as the way
            data should be send
        """
        self.status_message = self.status_message if self.status_message else (self.current_state.name if self.current_state else None)
        # ensure that some message is set 
        if len(self.data_outgoing) == 0:
            # no data to send, just return the default status with available=false
            return self.get_current_status(available=False)
        
        # else take the status from the data to be sent out next. The whole 
        # data, status combination gets popped in the next handle_outgoing 
        # function call by the next GET request from the controller, so here 
        # the status and data itself must still be kept in the list

        _, status = self.data_outgoing[0]
        self.last_send_status = status
        return status
        
    def handle_outgoing(self):
        """ When it is requested to send some data to other client/s
            it will be called to deliver the data to the FeatureCloud Controller.
            Then sets status variables (status_*) accordingly for the next data to send from
            self.data_outgoing

        """
        if len(self.data_outgoing) == 0:
            # no data to send
            return None
        
        # extract current data to be sent
        data, status = self.data_outgoing.pop(0)

        # check if the last status request was answered with the same status
        # as the data is supposed to be sent with
        # we just compare the JSON strings
        if status != self.last_send_status:
            raise Exception("Race condition error, the controller got sent a" +
                "different GET/status object that the one intended with this data object."+
                "Needed status object: {}, actual status object: {}".format(
                status, self.last_send_status))

        # status is fine, send data out
        return data

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
        self.status_message = self.current_state.name

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

    Attributes
    ----------
    app: App
    name: str

    Properties
    ----------
    is_coordinator: bool
    clients: list[str]
    id: str
    """

    def __init__(self):
        self._app = None
        self.name = None

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
        """ Boolean variable, if True the this AppState instance represents the
        coordinator. False otherwise.

        """
        return self._app.coordinator

    @property
    def clients(self):
        """ Contains a list of client IDs of all clients involved in the
        current learning run.

        """
        return self._app.clients

    @property
    def id(self):
        """ Contains the id of this client
        
        """
        return self._app.id
    
    @property
    def coordintor_id(self):
        """ Contains the id of the coordinator
        
        """
        return self._app.coordinatorID

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
                       use_dp=False, memo=None):
        """
        Waits for all participants (including the coordinator instance) 
        to send data and returns the aggregated value. Will try to convert
        each data piece to a np.array and aggregate those arrays.
        Therefore, this method only works for numerical data and all datapieces
        should be addable.

        Parameters
        ----------
        operation : SMPCOperation
            specifies the aggregation type
        use_smpc : bool, default=False
            if True, the data to be aggregated is expected to stem from an SMPC aggregation
        use_dp: bool, default=False
            if True, will assume that data was sent and modified with the
            controllers differential privacy capacities (with use_dp=true in the
            corresponding send function). This must be set in the receiving 
            function due to serialization differences with DP
        memo : str or None, default=None
            the string identifying a specific communication round. 
            Any app should ensure that this string is the same over all clients
            over the same communication round and that a different string is 
            used for each communication round. This ensures that no race 
            condition problems occur
        Returns
        -------
        aggregated value
        """
        if not memo:
            self._app.receive_counter += 1
            memo = f"GATHERROUND{self._app.receive_counter}"
        if use_smpc:
            return self.await_data(n=1, unwrap=True, is_json=True, memo=memo)  
              # Data is aggregated already
        else:
            data = self.gather_data(is_json=use_dp, memo=memo)
            return _aggregate(data, operation)  
              # Data needs to be aggregated according to operation

    def gather_data(self, is_json=False, use_smpc=False, use_dp=False, memo=None):
        """
        Waits for all participants (including the coordinator instance) to send data and returns a list containing the received data pieces. Only valid for the coordinator instance.

        Parameters
        ----------
        is_json : bool, default=False
            [deprecated] when data was sent via DP or SMPC, the data is sent in
            JSON serialization. This was used to indicate this but is now 
            DEPRICATED, use use_smpc/use_dp accordingly instead, they will take
            care of serialization automatically.
        use_smpc: bool, default=False
            Indicated whether the data that is gather was sent using SMPC.
            If this is not set to True when data was sent using SMPC, this 
            function ends up in an endless loop
        use_dp: bool, default=False
            if True, will assume that data was sent and modified with the
            controllers differential privacy capacities (with use_dp=true in the
            corresponding send function). This must be set in the receiving 
            function due to serialization differences with DP
        memo : str or None, default=None
            the string identifying a specific communication round. 
            Any app should ensure that this string is the same over all clients
            over the same communication round and that a different string is 
            used for each communication round. This ensures that no race 
            condition problems occur
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
        if not memo:
            self._app.receive_counter += 1
            memo = f"GATHERROUND{self._app.receive_counter}"
        return self.await_data(n, unwrap=False, is_json=is_json, use_dp=use_dp,
                               use_smpc=use_smpc, memo=memo)

    def await_data(self, n: int = 1, unwrap=True, is_json=False, 
                   use_dp=False, use_smpc=False, memo=None):
        """
        Waits for n data pieces and returns them. It is highly recommended to 
        use the memo variable when using this method

        Parameters
        ----------
        n : int, default=1
            number of data pieces to wait for. Is ignored when use_smpc is used
            as smpc data is aggregated by the controller, therefore only one
            data piece is given when using smpc
        unwrap : bool, default=True
            if True, will return the first element of the collected data (only useful if n = 1)
        is_json : bool, default=False
            [deprecated] when data was sent via DP or SMPC, the data is sent in
            JSON serialization. This was used to indicate this to deserailize
            the data correctly, but is now DEPRICATED, use use_smpc/use_dp
            accordingly instead, they will take care of serialization
            automatically. 
        use_dp : bool, default=False
            if True, will assume that data was sent and modified with the
            controllers differential privacy capacities (with use_dp=true in the
            corresponding send function). This must be set in the receiving 
            function due to serialization differences with DP
        use_smpc: bool, default=False
            if True, will ensure that n is set to 1 and the correct 
            serialization is used (SMPC uses JSON serialization)
        memo : str or None, default=None
            RECOMMENDED TO BE SET FOR THIS METHOD!
            the string identifying a specific communication round. The same
            string that is used in this call must be used before in the 
            corresponding sending functions.
            Any app should ensure that this string is the same over all clients
            over the same communication round and that a different string is 
            used for each communication round. This ensures that no race 
            condition problems occur.
        Returns
        -------
        list of data pieces (if n > 1 or unwrap = False) or a single data piece (if n = 1 and unwrap = True)
        """
        if use_smpc:
            n = 1
            is_json = True
        if use_dp:
            is_json = True
        if not memo and self._app.coordinator:
            # only increment for the coordinator to really avoid any p2p 
            # problems
            if (n == len(self._app.clients) and use_smpc==False) \
                or (n == len(self._app.clients) - 1 and use_smpc==False) \
                or use_smpc == True:
                # this is a gather/aggregate call, although in theory
                # (n==1 and is_json=True) could also be an SMPC gather call,
                # but it cannot be differentiate between that being an SMPC
                # gather call or an p2p with DP call
                self._app.receive_counter += 1
                memo = f"GATHERROUND{self._app.receive_counter}"

        try:
            memo = str(memo)
        except Exception as e:
            self._app.log(
                f"given memo cannot be translated to a string, ERROR: {e}", 
                LogLevel.Error)

        while True:
            num_data_pieces = 0
            if memo in self._app.data_incoming:
                num_data_pieces = len(self._app.data_incoming[memo])
            if num_data_pieces >= n:
                # warn if too many data pieces came in
                if num_data_pieces > n:
                    self._app.log(
                        f"await was used to wait for {n} data pieces, " + 
                        f"but more data pieces ({num_data_pieces}) were found. " +
                        f"Used memo is <{memo}>",
                        LogLevel.ERROR)
                    
                # extract and deseralize the data
                data = self._app.data_incoming[memo][:n]
                self._app.data_incoming[memo] = self._app.data_incoming[memo][n:]
                if len(self._app.data_incoming[memo]) == 0:
                    # clean up the dict regularly
                    del self._app.data_incoming[memo]

                if n == 1 and unwrap:
                    return _deserialize_incoming(data[0][0], is_json=is_json)
                else:
                    return [_deserialize_incoming(d[0], is_json=is_json) for d in data]

            sleep(DATA_POLL_INTERVAL)

    def send_data_to_participant(self, data, destination, use_dp=False, 
                                 memo=None):
        """
        Sends data to a particular participant identified by its ID. Should be
        used for any specific communication to individual clients. 
        For the communication schema of all clients/all clients except the 
        coordinator sending data to the coordinator, use send_data_to_coordinator

        Parameters
        ----------
        data : object
            data to be sent
        destination : str
            destination client ID, get this from e.g. self.clients
        use_dp : bool, default=False
            Whether to use differential privacy(dp) before sending out the data.
            To configure the hypterparameters of dp, use the configure_dp method
            before this method. The receiving method must also use the same 
            setting of the use_dp flag or there will be serialization problems
        memo : str or None, default=None
            RECOMMENDED TO BE SET FOR THIS METHOD!
            the string identifying a specific communication round. 
            This ensures that there are no race condition problems and the 
            correct data piece can be identified by the recipient of the 
            data piece sent with this function call. The recipient of this data
            must use the same memo to identify the data.

        """
        try:
            memo = str(memo)
        except Exception as e:
            self._app.log(
                f"given memo cannot be translated to a string, ERROR: {e}", 
                LogLevel.Error)
            
        data = _serialize_outgoing(data, is_json=use_dp)
        if destination == self._app.id and not use_dp:
            # In no DP case, the data does not have to be sent via the controller
            self._app.handle_incoming(data, client=self._app.id, memo=memo)
        else:
            # update the status variables and get the status object
            message = self._app.status_message if self._app.status_message else (self._app.current_state.name if self._app.current_state else None)
            dp = self._app.default_dp if use_dp else None
            self._app.status_message = message
            status = self._app.get_current_status(message=message, 
                        destination=destination, dp=dp, memo=memo,
                        available=True)
            self._app.data_outgoing.append((data, json.dumps(status, sort_keys=True)))

    def send_data_to_coordinator(self, data, send_to_self=True, use_smpc=False,
                                 use_dp=False, memo=None):
        """
        Sends data to the coordinator instance. Must be used by all clients
        or all clients except for the coordinator itself when no memo is given,
        as the automated memo used when using memo=None breaks otherwise.
        If any subset of clients should communicate with the coordinator,
        either define the memo or use 
        send_data_to_participant(destination=self.coordintor_id) with a memo.

        Parameters
        ----------
        data : object
            data to be sent
        send_to_self : bool, default=True
            if True, the data will also be sent internally to this instance (only applies to the coordinator instance)
        use_smpc : bool, default=False
            if True, the data will be sent as part of an SMPC aggregation step
        use_dp : bool, default=False
            Whether to use differential privacy(dp) before sending out the data.
            To configure the hypterparameters of dp, use the configure_dp method
            before this method. The receiving method must also use the same 
            setting of the use_dp flag or there will be serialization problems
        memo : str or None, default=None
            the string identifying a specific communication round. 
            This ensures that there are no race condition problems so that the 
            coordinator uses the correct data piece from each client for each
            communication round. This also ensures that workflows where 
            participants send data to the coordinator without waiting for a 
            response work
        """
        # if no memo is given (default), we use the counter from App
        if not memo:
            self._app.send_counter += 1
            memo = f"GATHERROUND{self._app.send_counter}"
        # ensure memo can be sent as a string
        try:
            memo = str(memo)
        except Exception as e:
            self._app.log(
                f"given memo cannot be translated to a string, ERROR: {e}", 
                LogLevel.Error)
            
        if use_smpc or use_dp:
            data = _serialize_outgoing(data, is_json=True)

        else:
            data = _serialize_outgoing(data, is_json=False)

        if self._app.coordinator and not use_smpc and not use_dp:
            # coordinator sending itself data, if that is wanted (send_to_self),
            # and neither dp nor smpc are used, the controller does not have to be used
            # for sending the data
            if send_to_self:
                self._app.handle_incoming(data, self._app.id, memo)
        else:
            # for SMPC and DP, the data has to be sent via the controller        
            if use_dp and self._app.coordinator:
                # give the coordinator as destination,
                # else, it will be interpreted as a broadcast action
                destination = self._app.id
            else:
                destination = None 
                # this is interpreted as to the coordinator
            message = self._app.status_message if self._app.status_message else (self._app.current_state.name if self._app.current_state else None)
            self._app.status_message = message
            smpc = self._app.default_smpc if use_smpc else None
            dp = self._app.default_dp if use_dp else None
            status = self._app.get_current_status(message=message, 
                        destination=destination, smpc=smpc, dp=dp, memo=memo,
                        available=True)
            self._app.data_outgoing.append((data, json.dumps(status, sort_keys=True)))

    def broadcast_data(self, data, send_to_self=True, use_dp = False, 
                       memo = None):
        """
        Broadcasts data to all participants (only valid for the coordinator instance).

        Parameters
        ----------
        data : object
            data to be sent
        send_to_self : bool
            if True, the data will also be sent internally to this coordinator instance
        use_dp : bool, default=False
            Whether to use differential privacy(dp) before sending out the data.
            To configure the hypterparameters of dp, use the configure_dp method
            before this method. The receiving method must also use the same 
            setting of the use_dp flag or there will be serialization problems
        memo : str or None, default=None
            the string identifying a specific communication round. 
            This ensures that there are no race condition problems so that the 
            participants and the coordinator can differentiate between this
            data piece broadcast and other data pieces they receive from the
            coordinator.
        """
        try:
            memo = str(memo)
        except Exception as e:
            self._app.log(
                f"given memo cannot be translated to a string, ERROR: {e}", 
                LogLevel.Error)
            
        if not self._app.coordinator:
            self._app.log('only the coordinator can broadcast data', level=LogLevel.FATAL)

        is_json = False
        if use_dp:
            is_json = True

        # serialize before broadcast
        data = _serialize_outgoing(data, is_json=use_dp)

        message = self._app.status_message if self._app.status_message else (self._app.current_state.name if self._app.current_state else None)
        self._app.status_message = message
        dp = self._app.default_dp if use_dp else None
        status = self._app.get_current_status(message=message, 
                        destination=None, dp=dp, memo=memo,
                        available=True)
        if send_to_self:
            self._app.handle_incoming(data, client=self._app.id, memo=memo)
        self._app.data_outgoing.append((data, json.dumps(status, sort_keys=True)))

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
            operation to perform for aggregation. Options are SMPCOperation.ADD and SMPCOperation.MULTIPLY
            SMPCOperation.MULTIPLY is still experimental and may lead to values 
            being 0 or integer overflows for many clients involved.
        serialization : SMPCSerialization, default=SMPCSerialization.JSON
            serialization to be used for the data, currently only the default Option (SMPCSerialization.JSON) is supported
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
        sensitivity: float, default = None
            describes the amount of privacy introduced by the function used on 
            the data that was used to create the model that is send with DP.
            Depends on the function or on the function and the data.
            If using a clippingVal, the sensitivity must not be defined.
        clippingVal : float, default = 10.0
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
            if noisetype == DPNoisetype.LAPLACE:
                delta = 0
            else:
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
                self._app.log("When using gauss noise, delta must be > 0",
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
