cwlVersion: v1.2
$graph:
  - class: Workflow
    id: physrisk-current
    label: OS Climate Physical Risk
    doc: >
      The OS Climate physical risk workflow will undertake a risk analysis on your asset portfolio of the potential impacts of climate change. According to the type of your asset, the workflow will analyse risks from chronic heat, inundation.

      This workflow requires the following columns: ID, latitude, longitude, asset_type, location
    requirements:
      NetworkAccess:
        networkAccess: true

    inputs:
      json_string:
        type: string
        doc: the file to transform
    outputs:
      - id: asset-result
        type: Directory
        outputSource:
          - get-impact/asset-result
    steps:
      get-impact:
        run: "#get-asset-impact"
        in:
          json_string: json_string
        out:
          - asset-result
  - class: CommandLineTool
    id: get-asset-impact
    requirements:
        NetworkAccess:
            networkAccess: true
        DockerRequirement:
            dockerPull: public.ecr.aws/z0u8g6n1/eodh:osc-data-rcr
    baseCommand: get_asset_impact.py
    inputs:
        json_string:
            type: string
            inputBinding:
                prefix: --json_string=
                separate: false
                position: 4
    outputs:
        asset-result:
            type: Directory
            outputBinding:
                glob: "./asset_output"