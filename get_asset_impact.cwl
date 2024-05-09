cwlVersion: v1.2
class: CommandLineTool
id: get_asset_impact
requirements:
  NetworkAccess:
    networkAccess: true
  DockerRequirement:
    dockerImageId: physrisk-cli:0.1
baseCommand: get_asset_impact.py
inputs:
  json_file:
    type: File?
    inputBinding:
      prefix: --json_file=
      separate: false
      position: 4
  flat:
    type: boolean?
    inputBinding:
      prefix: --flat
      separate: false
      position: 5
outputs:
  file_out:
    type: stdout
stdout: output.json