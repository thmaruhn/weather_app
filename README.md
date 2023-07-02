# Weather App

Weather app that uses an [API](https://www.visualcrossing.com/weather-data-editions) to get weather information and pushes the results to a BigQuery DB

## Input parameters 

| Parameter   | Label | Format     |   Note|
|--------------|-----------|-----------|------------|
|`START_DATE`| City | `string`| select date from calendar|
|`END_DATE`|  From date | `string`| select date from calendar|
|`LOCATION`| To date | `string`| If location not found, error message should appear|
|`API_KEY`| API Key| `string`| API key generated from free account at Visualcrossing |
|`GOOGLE_APPLICATION_CREDENTIALS_PATH`| Google Application Credentials Path | `string`| default set to currently used DB|
|`BIG_QUERY_TARGET_ID`| BigQuery Target ID | `string (Format: “PROJECT.DATASET.TABLE”)`| upload .json file with authentification information|

## Output

After successful entry of input, the date sent should appear as .json. In addition, last 5 entries of DB are shown, based on runtime of service call in timezone of the
requested location

The following .json is send to the BigQueryDB

```json
{
    "resolved_address": string,
    "start_date": date,
    "query_cost": number,
    "average_temp": number,
    "max_cloudcover": number,
    "fog": boolean,
    "days_with_drizzle": number,
    "runtime_timestamp": timestamp
}
```
Notes/Assumptions:
- days_with_drizzle: based on preciptype and possible values of: rain, snow, freezingrain and ice. Rain and freezing rain countes as day with drizzle
- fog: based on visibility and [Wikipedia](https://en.wikipedia.org/wiki/Visibility#Fog,_mist,_haze,_and_freezing_drizzle) entry that 'The international definition of fog is a visibility of less than 1 km (3,300 ft);'