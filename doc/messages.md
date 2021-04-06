## Messages 

### Commands

Connect Bt Device

```json
{
    "bt_device_connect" : "device ADDR"
}

{
    "bt_device_disconnect" : "device ADDR"
}
```


Sink/Source selection

```json
{
    "audio_default_sink" : "pa sink name"
}

{
    "audio_default_source" : "pa source name"
}
```


Volumes

```json
{
    "audio_set_sink_sink_volume" : {
        "sink_name" : "vol_level"
    }
}

{
    "audio_set_source_volume" : {
        "source_name" : "vol_level"
    }
}
```


### Status

```json
{
    "oxe_spot_status" : "Unknown|Ready|Not Started"
}


```json
{
    "bt_speaker_status" : {
        "addr"   : "device addr",
        "status" : "Unknown|Not Connected|Discovering|Pairing|Connecting|Connected"
    }
}


```
