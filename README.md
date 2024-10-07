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
toil-cwl-runner get_asset_impact.cwl#get-asset-impact-workflow --json_file='https://example.com/file.json'
```

This should output a directory called `asset_output` in the same folder it was run from with the results in a file called `result.json`.