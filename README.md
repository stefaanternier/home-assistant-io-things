 


[![GitHub Activity](https://img.shields.io/github/commit-activity/y/stefaanternier/home-assistant-io-things?style=for-the-badge)](https://github.com/stefaanternier/home-assistant-io-things/commits/main)

# Io-Things sensors

Component for tracking the state of Io-Things sensors via the only API. 

**Note:** Using this component only makes sense if you have purchased Io-Things sensors and if you have access to the Io-Things portal.


## Example configs:

```yaml
iothings:
  access_token: your_io_things_api_key
  
sensor:
  - platform: iothings
    unique_id: C50000
  - platform: iothings
    unique_id: C50001
```

