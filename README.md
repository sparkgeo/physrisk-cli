# Physrisk CLI

Command Line Interface for the [Physrisk Lib](https://github.com/os-climate/physrisk)

## Creating the docker image

```bash
cd src/
docker build --build-arg OSC_S3_ACCESS_KEY=<access_key> --build-arg OSC_S3_SECRET_KEY=<secret_key> -t physrisk-cli:0.1 .
```

## Running the CWL

### Example Commands

```bash
toil-cwl-runner get_asset_impact.cwl#get-asset-impact-workflow --json_string='{ "type": "FeatureCollection", "features": [ { "type": "Feature", "properties": { "asset_class": "IndustrialActivity", "type": "Construction", "location": "Asia" }, "geometry": { "type": "Point", "coordinates": [65.119, 32.322] } }, { "type": "Feature", "properties": { "asset_class": "IndustrialActivity", "type": "Construction", "location": "South America" }, "geometry": { "type": "Point", "coordinates": [-68.5982, -39.1009] } } ], "properties": { "include_asset_level": true, "include_calc_details": true, "include_measures": true, "years": [ 2030, 2040 ], "scenarios": [ "ssp126", "ssp245" ] }}'
```

This should output a directory called `asset_output` in the same folder it was run from with the results in a file called `result.json`.