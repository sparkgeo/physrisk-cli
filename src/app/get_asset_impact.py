"""
This module is used to make a request to get hazard data. It includes functions
to parse command-line arguments and make the request.
The module uses the Container from the physrisk package to make the request.
"""

import argparse
import json
import logging
import os

from physrisk.container import Container

logging.basicConfig(level=logging.INFO)


def make_request(params: dict):
    """
    Makes a request to get hazard data.

    This function creates a request dictionary with the provided parameters,
    then uses the requester from the Container to make the request. If an error
    occurs during the request, it is logged and the function returns None.

    Args:
        params (dict): The parameters for the request. These will be
            included in the 'items' list of the request dictionary.

    Returns:
        dict: The response from the request, or None if an error occurred.
    """

    try:
        requester = Container.requester
        request_id = "get_asset_impact"
        params = json.loads(
            '{"assets":{"items":[{"asset_class":"IndustrialActivity","type":"Construction","location":"Asia","latitude":32.322,"longitude":65.119},{"asset_class":"IndustrialActivity","type":"Construction","location":"South America","latitude":-39.1009,"longitude":-68.5982}]},"include_asset_level":true,"include_calc_details":true,"include_measures":true,"years":[2030,2040],"scenarios":["ssp126","ssp245"]}'
        )
        params["group_ids"] = ["osc"]
        return requester().get(request_id=request_id, request_dict=params)
    except Exception as e:
        logging.error("Error in making request: %s", e)
        return None


def parse_arguments():
    """
    Parses command-line arguments for the request.

    Returns:
        argparse.Namespace: An object that holds the parsed arguments as
        attributes.
    """
    parser = argparse.ArgumentParser(description="Make a request.")
    parser.add_argument("--json", type=str, help="JSON string with request parameters")
    return parser.parse_args()


if __name__ == "__main__":
    if not os.getenv("OSC_S3_ACCESS_KEY" or not os.getenv("OSC_S3_SECRET_KEY")):
        logging.error("AWS credentials not found")
        exit(1)
    args = parse_arguments()
    request_params = json.loads(args.json)
    response = make_request(request_params)
    if response is not None:
        print(response)
    else:
        logging.error("Request failed")
