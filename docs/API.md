# API specifications

> Version 1.1.0

This is a sample client of a federated computation in FeatureCloud.

## Path Table

| Method | Path | Description |
| --- | --- | --- |
| POST | [/setup](#postsetup) | Setup the local client and trigger start of local execution |
| GET | [/status](#getstatus) | Status of the local client |
| GET | [/data](#getdata) | Receive data from coordinator or other clients |
| POST | [/data](#postdata) | Send data to coordinator or broadcast data from coordinator to other clients |

## Path Details

***

### [POST]/setup

- Summary  
Setup the local client and trigger start of local execution

#### RequestBody

- application/json

```ts
{
  id: string
  coordinator: boolean
  clients?: string[]
}
```

#### Responses

- 200 Success

***

### [GET]/status

- Summary  
Status of the local client

#### Responses

- 200 Success

`application/json`

```ts
{
  available: boolean
  finished: boolean
  message?: string
  progress?: number
  state?: enum[running, error, action_required]
  destination?: string
  smpc: {
    operation?: enum[add]
    serialization?: enum[json]
    shards?: number
    exponent?: number
  }
}
```

***

### [GET]/data

- Summary  
Receive data from coordinator or other clients

#### Responses

- 200 Success

`application/octet-stream`

```ts
{
  "type": "string",
  "format": "binary"
}
```

***

### [POST]/data

- Summary  
Send data to coordinator or broadcast data from coordinator to other clients

#### RequestBody

- application/octet-stream

```ts
{
  "type": "string",
  "format": "binary"
}
```

#### Responses

- 200 Success
