from physrisk_cli_logger import logger


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
    logger.info("Converting request to PhysRisk format")
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
            "include_asset_level": True,
            "include_calc_details": True,
            "include_measures": True,
            "years": [2030, 2040, 2050],
            "scenarios": ["ssp126", "ssp245", "ssp585"],
        }

        return json_out
    except KeyError:
        logger.exception("Key error while converting request to PhysRisk format")
    except Exception:
        logger.exception(
            "An error occurred while converting request to PhysRisk format"
        )


def replace_values_with_null(obj):
    """
    Recursively replaces specific values in a nested
    structure (dicts and lists) with None. Specifically,
    replaces -9999 with None, and -1 with None if the key
    is 'score'.

    Parameters:
    obj (dict | list): The input nested structure.

    Returns:
    dict | list: The modified structure with specified
    values replaced by None.
    """
    if isinstance(obj, dict):
        return {
            k: (
                replace_values_with_null(v)
                if isinstance(v, (dict, list))
                else (None if (v == -9999 or (k == "score" and v == -1)) else v)
            )
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [
            (
                replace_values_with_null(item)
                if isinstance(item, (dict, list))
                else (None if item == -9999 else item)
            )
            for item in obj
        ]
    else:
        return obj


def convert_response_from_physrisk_format(
    json_in: dict, original_geojson: dict
) -> dict:
    """
    This function takes a JSON input containing asset impacts and risk measures
    from the PhysRisk format and integrates this data into a provided GeoJSON structure.
    Each asset's impacts and risk measures are added to the corresponding feature in
    the GeoJSON. The 'properties' key of the original GeoJSON is removed in the process.

    Parameters:
    - json_in (dict): The input JSON in PhysRisk format, containing 'asset_impacts'
    and 'risk_measures'.
    - original_geojson (dict): The original GeoJSON structure to which the converted
    data will be added.

    Returns:
    - dict: The modified GeoJSON structure with added asset impacts and risk measures
    for each feature.

    Raises:
    - KeyError: If a required key is missing in the input JSON.
    - Exception: For any other errors that occur during the conversion process.
    """
    logger.info("Converting response from PhysRisk format")
    try:
        score_based_measure_set_defn = score_based_measure_set_defn = json_in.get(
            "risk_measures", {}
        ).get("score_based_measure_set_defn")
        for asset_no, asset_impact in enumerate(json_in["asset_impacts"]):
            impacts = {}
            measures = {}
            # Get the measures
            for measure_scores in json_in["risk_measures"]["measures_for_assets"]:
                measures_key = measure_scores["key"]
                val = measure_scores["measures_0"][asset_no]
                scores = measure_scores["scores"][asset_no]
                measures.setdefault(measures_key["hazard_type"], {}).setdefault(
                    measures_key["scenario_id"], {}
                ).setdefault(measures_key["year"], {"measures": val, "score": scores})
            # Get the impacts
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
                impacts.setdefault(key["hazard_type"], {}).setdefault(
                    key["scenario_id"], {}
                )[key["year"]] = props

            original_geojson["features"][asset_no]["asset_impacts"] = impacts
            original_geojson["features"][asset_no]["risk_measures"] = measures

            # Change -9999 to null values
            original_geojson = replace_values_with_null(original_geojson)
            original_geojson[
                "score_based_measure_set_defn"
            ] = score_based_measure_set_defn

        return original_geojson
    except KeyError:
        logger.exception("Key error while converting response from PhysRisk format")
    except Exception:
        logger.exception(
            "An error occurred while converting response from PhysRisk format"
        )


def convert_response_from_physrisk_format_to_flat(json_in: dict) -> dict:
    """
    Converts a response from PhysRisk format to a flat GeoJSON format.

    Args:
        json_in (dict): The input JSON in PhysRisk format.

    Returns:
        dict: The converted JSON in GeoJSON format.Each feature in the 'features' list
        represents an asset. The 'properties' of each feature is a dictionary with
        two keys: 'asset_impacts' and 'risk_measures'. 'asset_impacts' is a dictionary
        where the keys are strings combining the year, scenario id, and hazard type,
        'risk_measures' is a dictionary where the keys are strings combining the year,
        scenario id, and hazard type, and the values are the corresponding scores.

    Raises:
        KeyError: If a required key is missing in the input JSON.
    """
    logger.info("Converting response from PhysRisk format to flat")
    try:
        json_out = {"type": "FeatureCollection", "features": []}

        for asset_no, asset_impact in enumerate(json_in["asset_impacts"]):
            impacts = {}
            measures = {}
            # Get the measures
            for measure_scores in json_in["risk_measures"]["measures_for_assets"]:
                measures_key = measure_scores["key"]
                key = f"{measures_key['year']}_{measures_key['scenario_id']}_{measures_key['hazard_type']}"
                scores = measure_scores["scores"][asset_no]
                measures[key] = scores
            # Get the impacts
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
                props_key = f"{key['year']}_{key['scenario_id']}_{key['hazard_type']}"
                impacts[props_key] = props

            json_out["features"].append(
                {
                    "type": "Feature",
                    "properties": {"asset_impacts": impacts, "risk_measures": measures},
                    "geometry": {"type": "Point", "coordinates": [1, 2]},
                }
            )

        return json_out
    except KeyError:
        logger.exception(
            "Key error while converting response from PhysRisk format to flat"
        )
    except Exception:
        logger.exception(
            "An error occurred while converting response from PhysRisk format to flat"
        )
