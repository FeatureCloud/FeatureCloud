# API specifications

> Version 1.1.0

This is a sample client of a federated computation in FeatureCloud.

A sample client should implement the following three functionalities via 
implementing the API given here:
1. Setup: The local client gets informed via [GET/setup](#postsetup) about whether
   it is the coordinator or not, about it's own id and about the ids of all 
   involved clients.
2. Sending data: The local client gets asked if it has any data to be sent and
   the conditions of the relay of data via the [GET/status](#getstatus) request.
   If the response to that request contains `available:true`, a followup 
   [GET/data](#getdata) request is send to retrieve the data for relay.
3. Receiving data: Receiving the data sent in step 2 from another client
   happens via the [POST/data?client](#postdataclient) call.

The sample client should listen to localhost on port 5000.

## Path Table

| Method | Path | Description |
| --- | --- | --- |
| POST | [/setup](#postsetup) | Setup the local client and trigger start of local execution |
| GET | [/status](#getstatus) | Status of the local client, information on how to relay data to other clients |
| GET | [/data](#getdata) | Request data from local client for relay to other clients |
| POST | [/data?client](#postdataclient) | Posts data from coordinator or other clients to local client |

## Path Details

### [POST]/setup
- Summary  

Setup the local client and trigger start of local execution.

- Details

Posts the information about which id the current client posses, if it is the
coordinator and the ids of all clients involved.
This information can later be used as information on where to send data
and which role this client takes (coordinator or participant).

#### RequestBody

- application/json

```ts
{
  id: string
  coordinator: boolean
  clients: string[]
}
```

#### Responses

- 200 Success

***

### [GET]/status
- Summary  

Status of the local client, containing information about how data should be 
relayed to other client(s).

Local Client -> Relay Server

- Details

The response of this request gives information about how data should be sent.
As soon as available is true, a follow up [\[GET\]/data](#getdata) request is 
sent. The data fetched with that [\[GET\]/data](#getdata) request is send 
according to the information given in this [\[GET\]/status](#getstatus) request.

#### Responses

- 200 Success

`application/json`

```ts
{
  available: boolean // if set to true, a follow up GET/data request is send
  finished: boolean
  message?: string
  progress?: number
  state?: enum[running, error, action_required]
  destination?: string 
    // destination is the id of the client the data should be sent to.
    // if no destination is given the following applies: 
    // If the data comes from the coordinator it's
    // broadcast to all clients, if the data comes from any client the data
    // is send to the coordinator.
    // When using SMPC, destination does not have to be given and data is sent
    // correctly automatically
  smpc?: {
    operation: enum[add, multiply] 
    serialization?: enum[json] // default is json
    shards?: number // default is number of participants including coordinator
    exponent?: number // default is 8
  }
  dp?: {
    serialization?: enum[json] // default is json
    noisetype?: enum[laplace, gauss] // default is laplace
    epsilon?: float // default is 0.99999
    delta?: float // default is 0 for laplace noise and 0.01 for gauss noise
    sensitivity?: float 
    clippingVal?: float 
      // default is 10.0 and only set if neither
      // clippingVal nor sensitivity are given
  }
}
```

***

### [GET]/data

- Summary  

Receive data from the local client for relay as specified in previous response 
to [\[GET\]/status](#getstatus)

Local Client -> Relay Server

- Details

This request is the follow up request after a [\[GET\]/status](#getstatus) that
got answered with the parameter `available: true`. The response can contain any
data and is send according to the information given in the
previous [\[GET\]/status](#getstatus) response. All information is send 
encrypted.

#### Responses

- 200 Success

`application/octet-stream`

```ts
{
  // any data given in application/octet-stream format, 
  // must comply serialization format for SMPC/DP (JSON).
}
```

***

### [POST]/data?client

- Summary

Any data sent by other clients to the local client is given to the local client
via the RequestBody of this call

Relay Server -> Local Client

- Details

The query variable client contains the clientID of the client that sent the data
that the local client is receiving via this call.
Furthermore, the RequestBody contains the data that another client sent.

#### Query
The variable `client` of the query string contains the `clientID` of the remote
client which send the data to the local client. For SMPC, the variable `client`
has no relevance as the data sent in the RequestyBody is already aggregated 
data.

#### RequestBody

- application/octet-stream

```ts
{
  // any data given in application/octet-stream format, 
  // if send via SMPC/DP, will comply with the corresponding serialization
  // format (JSON)
}
```

#### Responses

- 200 Success
