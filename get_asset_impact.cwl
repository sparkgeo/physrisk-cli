cwlVersion: v1.2
$namespaces:
  s: https://schema.org/
s:softwareVersion: 0.0.4
schemas:
  - http://schema.org/version/9.0/schemaorg-current-http.rdf
$graph:
  - class: Workflow
    id: get-asset-impact-workflow
    label: get asset impact
    doc: get asset impact
    requirements:
      NetworkAccess:
        networkAccess: true
      InlineJavascriptRequirement: {}

    inputs:
      geojson:
        type: string
        doc: the file to transform
    outputs:
      - id: asset-result
        type: Directory
        outputSource:
          - get-impact/asset-result
      - id: actual-result
        type: string
        outputSource: get-impact/actual-result
    steps:
      parse_json:
        run: "#parse-json"
        in:
          json_input: geojson
        out: [parsed_json]
      get-impact:
        run: "#get-asset-impact"
        in:
          geojson: parse_json/parsed_json
        out:
          - asset-result
          - actual-result
  - class: CommandLineTool
    id: get-asset-impact
    requirements:
        NetworkAccess:
            networkAccess: true
        DockerRequirement:
          dockerImageId: physrisk-cli:0.1
    baseCommand: get_asset_impact.py
    inputs:
        geojson:
            type: string
            inputBinding:
                prefix: --geojson=
                separate: false
                position: 4
    outputs:
        asset-result:
            type: Directory
            outputBinding:
                glob: "./asset_output"
        actual-result:
          type: string

  - class: ExpressionTool
    id: parse-json

    requirements:
      InlineJavascriptRequirement: {}

    inputs:
      json_input:
        type: string
        doc: "A large JSON string input from an API"

    outputs:
      parsed_json:
        type: string

    expression: >
      ${
        // Parse the input JSON string
        var parsed = JSON.parse(inputs.json_input);
        // Convert the parsed JSON object back to a JSON string
        var jsonString = JSON.stringify(parsed);
        // Return the JSON string
        return { "parsed_json": jsonString };
      }