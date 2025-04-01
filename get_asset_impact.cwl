cwlVersion: v1.2
$graph:
  - class: Workflow
    id: physrisk-filter
    label: OS Climate Physical Risk
    doc: >
      The OS Climate physical risk workflow will undertake a risk analysis on your asset portfolio of the potential impacts of climate change. According to the type of your asset, the workflow will analyse risks from chronic heat, inundation.

      This workflow requires the following columns: ID, latitude, longitude, asset_type, location
    requirements:
      ResourceRequirement:
        coresMax: 2
        ramMax: 4096
      NetworkAccess:
        networkAccess: true
      EnvVarRequirement:
        envDef:
          AWS_DEFAULT_REGION: "eu-west-2"
    inputs:
      assets:
        type: string
        doc: The geojson file
    outputs:
      - id: asset-result
        type: Directory
        outputSource:
          - get-impact/asset-result
    steps:
      get-impact:
        run: "#get-asset-impact"
        in:
          assets: assets
        out:
          - asset-result
  - class: CommandLineTool
    id: get-asset-impact
    requirements:
        NetworkAccess:
            networkAccess: true
        DockerRequirement:
            dockerPull: public.ecr.aws/z0u8g6n1/eodh:15
    baseCommand: get_asset_impact.py
    inputs:
        assets:
            type: string
            inputBinding:
                prefix: --assets=
                separate: false
                position: 4
    outputs:
        asset-result:
            type: Directory
            outputBinding:
                glob: .