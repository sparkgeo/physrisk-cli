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


def convert_response_from_physrisk_format(json_in: dict) -> dict:
    """
    Converts a response from PhysRisk format to GeoJSON format.

    Args:
        json_in (dict): The input JSON in PhysRisk format.

    Returns:
        dict: The converted JSON in GeoJSON format.

    Raises:
        KeyError: If a required key is missing in the input JSON.
    """
    try:
        json_out = {"type": "FeatureCollection", "features": []}

        for asset_impact in json_in["asset_impacts"]:
            properties = {}
            for impact in asset_impact["impacts"]:
                key = impact["key"]
                props = {
                    "impact_distribution": {
                        "bin_edges": impact["impact_distribution"]["bin_edges"],
                        "probabilities": impact["impact_distribution"]["probabilities"],
                    },
                    "impact_exceedance": {
                        "exceed_probabilities": impact["impact_exceedance"][
                            "exceed_probabilities"
                        ],
                        "values": impact["impact_exceedance"]["values"],
                    },
                    "impact_mean": impact["impact_mean"],
                    "impact_std_deviation": impact["impact_std_deviation"],
                    "impact_type": impact["impact_type"],
                }
                properties.setdefault(key["hazard_type"], {}).setdefault(
                    key["scenario_id"], {}
                )[key["year"]] = props

            json_out["features"].append(
                {
                    "type": "Feature",
                    "properties": properties,
                    "geometry": {"type": "Point", "coordinates": [1, 2]},
                }
            )

        return json_out
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
