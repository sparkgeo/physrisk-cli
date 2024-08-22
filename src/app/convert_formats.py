import re

from physrisk_cli_logger import logger
from shortuuid import ShortUUID


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


def scoreText(score: int) -> str:
    """
    Converts a numerical score into a descriptive text string.

    This function takes an integer score and returns a corresponding
    descriptive text string based on predefined categories.
    The categories are as follows:
    - 0: "No data"
    - 1: "Low"
    - 2: "Medium"
    - 3: "High"
    - 4: "Red flag"
    Any other score will default to "No data".

    Parameters:
    - score (int): The numerical score to be converted.

    Returns:
    - str: The descriptive text corresponding to the given score.
    """
    match score:
        case 0:
            return None
        case 1:
            return "Low"
        case 2:
            return "Medium"
        case 3:
            return "High"
        case 4:
            return "Red flag"
        case _:
            return None


def convert_scenario_id_string(scenario_id: str) -> str:
    """
    Converts a scenario ID string from a compact form to a formatted form.

    If the scenario ID starts with "ssp", it converts it to the form "SSP1-2.6".
    Otherwise, it returns the scenario ID unchanged.

    Args:
        scenario_id (str): The scenario ID string to be converted.

    Returns:
        str: The formatted scenario ID string.
    """
    if scenario_id.startswith("ssp"):
        return f"{(scenario_id[0:3]).upper()}{scenario_id[3]}-{scenario_id[4]}.{scenario_id[5]}"
    else:
        return scenario_id


def pascal_to_words(pascal_str):
    """
    Converts a PascalCase string into a string of words with each word capitalized.

    Args:
        pascal_str (str): The PascalCase string to be converted.

    Returns:
        str: A string of words with each word capitalized, separated by spaces.

    Example:
        >>> pascal_to_words("PascalCaseString")
        'Pascal Case String'
    """
    # Use regex to find word boundaries
    words = re.findall(r"[A-Z][a-z]*", pascal_str)
    return " ".join(word.capitalize() for word in words)


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
            combined_data = {}

            for impact in asset_impact["impacts"]:
                key = impact["key"]
                hazard_type = key["hazard_type"]
                hazard_type = pascal_to_words(hazard_type)
                scenario_id = key["scenario_id"]
                scenario_id = convert_scenario_id_string(scenario_id)
                year = key["year"]

                if hazard_type not in combined_data:
                    combined_data[hazard_type] = {}
                if scenario_id not in combined_data[hazard_type]:
                    combined_data[hazard_type][scenario_id] = {}
                if year not in combined_data[hazard_type][scenario_id]:
                    combined_data[hazard_type][scenario_id][year] = {
                        "impact_distribution": None,
                        "impact_exceedance": None,
                        "impact_mean": None,
                        "impact_std_deviation": None,
                        "impact_type": None,
                        "measures": None,
                        "score": None,
                    }

                combined_data[hazard_type][scenario_id][year].update(
                    {
                        "impact_distribution": {
                            "bin_edges": impact["impact_distribution"]["bin_edges"],
                            "probabilities": impact["impact_distribution"][
                                "probabilities"
                            ],
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
                )

            # Get the measures
            for measure_scores in json_in["risk_measures"]["measures_for_assets"]:
                measures_key = measure_scores["key"]
                hazard_type = measures_key["hazard_type"]
                hazard_type = pascal_to_words(hazard_type)
                scenario_id = measures_key["scenario_id"]
                scenario_id = convert_scenario_id_string(scenario_id)
                year = measures_key["year"]
                val = measure_scores["measures_0"][asset_no]
                if val == -9999:
                    val = None
                scores = measure_scores["scores"][asset_no]
                scores = scoreText(scores)

                if hazard_type not in combined_data:
                    combined_data[hazard_type] = {}
                if scenario_id not in combined_data[hazard_type]:
                    combined_data[hazard_type][scenario_id] = {}
                if year not in combined_data[hazard_type][scenario_id]:
                    combined_data[hazard_type][scenario_id][year] = {
                        "impact_distribution": None,
                        "impact_exceedance": None,
                        "impact_mean": None,
                        "impact_std_deviation": None,
                        "impact_type": None,
                        "measures": None,
                        "score": None,
                    }

                combined_data[hazard_type][scenario_id][year].update(
                    {"measures": val, "score": scores}
                )

            original_geojson["features"][asset_no]["asset_impacts"] = combined_data
            original_geojson["features"][asset_no]["properties"][
                "id"
            ] = ShortUUID().random(length=8)

            original_geojson[
                "score_based_measure_set_defn"
            ] = score_based_measure_set_defn
            original_geojson["response_version"] = "0.0.5"

        return original_geojson
    except KeyError:
        logger.exception("Key error while converting response from PhysRisk format")
    except Exception:
        logger.exception(
            "An error occurred while converting response from PhysRisk format"
        )
