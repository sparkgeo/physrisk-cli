cwlVersion: v1.2
class: CommandLineTool
id: get_asset_impact
requirements:
  NetworkAccess:
    networkAccess: true
  DockerRequirement:
    dockerPull: public.ecr.aws/c9k5s3u3/osc-physrisk:latest
baseCommand: get_asset_impact.py
inputs:
  json_file:
    type: File?
    inputBinding:
      prefix: --json_file=
      separate: false
      position: 4
outputs:
  file_out:
    type: stdout
stdout: output.json