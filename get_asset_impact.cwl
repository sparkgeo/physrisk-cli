cwlVersion: v1.2
$graph:
  - class: Workflow
    id: get-asset-impact-workflow-textscores
    label: get asset impact
    doc: get asset impact
    requirements:
      NetworkAccess:
        networkAccess: true

    inputs:
      json_file:
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
          json_file: json_file
        out:
          - asset-result
  - class: CommandLineTool
    id: get-asset-impact
    requirements:
        NetworkAccess:
            networkAccess: true
        DockerRequirement:
            dockerPull: public.ecr.aws/z0u8g6n1/eodh:text_score
    baseCommand: get_asset_impact.py
    inputs:
        json_file:
            type: string
            inputBinding:
                prefix: --json_file=
                separate: false
                position: 4
    outputs:
        asset-result:
            type: Directory
            outputBinding:
                glob: "./asset_output"