# Physrisk CLI

Command Line Interface for the [Physrisk Lib](https://github.com/os-climate/physrisk)

## Creating the docker image

```bash
cd src/
docker build --build-arg OSC_S3_ACCESS_KEY=<access_key> --build-arg OSC_S3_SECRET_KEY=<secret_key> -t physrisk-cli:0.1 .
```

## Running the CWL

### Example files

input.json

```json
{
    "json_file": {
        "class": "File",
        "path": "request.json"
    }
}
```

request.json

```json
{
    "assets": {
        "items": [
            {
                "asset_class": "IndustrialActivity",
                "type": "Construction",
                "location": "Asia",
                "latitude": 32.322,
                "longitude": 65.119
            },
            {
                "asset_class": "IndustrialActivity",
                "type": "Construction",
                "location": "South America",
                "latitude": -39.1009,
                "longitude": -68.5982
            }
        ]
    },
    "include_asset_level": true,
    "include_calc_details": true,
    "include_measures": true,
    "years": [
        2030,
        2040
    ],
    "scenarios": [
        "ssp126",
        "ssp245"    ]
}
```

### Example Commands

```bash
toil-cwl-runner get_asset_impact.cwl input.json
```

This should output a file called `output.json` in the same folder it was run from with the results in.