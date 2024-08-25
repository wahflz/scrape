# Amazon Jobs
Periodically checks the Amazon Warehouse Jobs website for local jobs. This
requires config.yml.

## Example config.yml
```yaml
amazon:
  zips:
      - '55555'
      - '77777'

filters:
  - city: 'Seattle'
    state: 'GA'
    code: 'FC'
  - city: '*'
    state: 'FL'
    code: '*'

pushover:
  api_key: 'API_KEY'
  user_key: 'USER_KEY'

```