# Amazon Jobs
Periodically checks the Amazon Warehouse Jobs website for local jobs. This
requires config.yml.

## Example config.yml
```yaml
amazon:
  zip: '30214'
  distance: 30
  cities:
    - 'Newnan'
    - 'Moreland'

pushover:
  api_key: 'API_KEY'
  user_key: 'USER_KEY'

```