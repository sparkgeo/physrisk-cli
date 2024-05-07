def convert_request_to_physrisk_format(json_in: dict) -> dict:
    """
    Converts a GeoJSON object to the new format.

    Args:
        json_in (dict): The input GeoJSON object.

    Returns:
        dict: The converted object in the new format.

    Raises:
        KeyError: If a required key is missing in the input object.
        Exception: If any other error occurs.
    """
    try:
        items = [
            {
                "asset_class": feat["properties"]["asset_class"],
                "type": feat["properties"]["type"],
                "location": feat["properties"]["location"],
                "latitude": feat["geometry"]["coordinates"][1],
                "longitude": feat["geometry"]["coordinates"][0],
            }
            for feat in json_in["features"]
        ]

        json_out = {
            "assets": {"items": items},
            "include_asset_level": json_in["properties"].get("include_asset_level"),
            "include_calc_details": json_in["properties"].get("include_calc_details"),
            "include_measures": json_in["properties"].get("include_measures"),
            "years": json_in["properties"].get("years"),
            "scenarios": json_in["properties"].get("scenarios"),
        }

        return json_out
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
