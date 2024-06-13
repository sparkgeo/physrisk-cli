cwlVersion: v1.0
class: ExpressionTool

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
