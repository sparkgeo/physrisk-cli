#! /usr/local/bin/python

"""
This module is used to make a request to get hazard data. It includes functions
to parse command-line arguments and make the request.
The module uses the Container from the physrisk package to make the request.
"""

import argparse
import json
import logging
import os

import requests
from convert_formats import (
    convert_request_to_physrisk_format,
    convert_response_from_physrisk_format,
    convert_response_from_physrisk_format_to_flat,
)
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
    # parser.add_argument("--json", type=str, help="JSON string with request parameters")
    parser.add_argument(
        "--json_file", type=str, help="Path to the JSON file with request parameters"
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Optional argument to flatten the JSON output",
    )
    return parser.parse_args()


def get_coord_list(request: dict):
    """
    Extracts the coordinates from the request parameters.

    Args:
        request_params (dict): The request parameters.

    Returns:
        list: A list of the coordinates.
    """
    try:
        return [feat["geometry"]["coordinates"] for feat in request["features"]]
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_catalog() -> dict:
    return {
        "stac_version": "1.0.0",
        "id": "asset-vulnerability-catalog",
        "type": "Catalog",
        "description": "OS-C physrisk asset vulnerability catalog",
        "links": [
            {"rel": "self", "href": "./catalog.json"},
            {"rel": "root", "href": "./catalog.json"},
        ],
    }


if __name__ == "__main__":
    if not os.getenv("OSC_S3_ACCESS_KEY") or not os.getenv("OSC_S3_SECRET_KEY"):
        logging.error("AWS credentials not found")
        exit(1)
    args = parse_arguments()
    # request_params = json.loads(args.json)
    print(f"I am checking here {args.json_file}")
    if "http" in args.json_file:
        url = args.json_file
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(
                f"request to get the content of the input JSON {args.json_file} over HTTP failed : {response.text}"
            )
        request_params = json.loads(response.content)
    else:
        with open(args.json_file, "r", encoding="utf-8") as file:
            request_params = json.load(file)
    # Getting the coordinates from the request
    coord_list = get_coord_list(request_params)
    # Convert the request to the format expected by the physrisk package
    request_params = convert_request_to_physrisk_format(request_params)
    # Make the request
    response = make_request(request_params)
    # convert string to json
    response = json.loads(response)
    # Convert the response to the geojson format
    if args.flat:
        response_geojson = convert_response_from_physrisk_format_to_flat(response)
    else:
        response_geojson = convert_response_from_physrisk_format(response)
    # Adding the coordinates to the response
    for feat in response_geojson["features"]:
        feat["geometry"]["coordinates"] = coord_list.pop(0)
    if response_geojson is not None:
        print("##ASSET_OUTPUT_STARTS##")
        print(json.dumps(response_geojson))
        print('##ASSET_OUTPUT_ENDS""')
    else:
        logging.error("Request failed")

    os.makedirs("asset_output", exist_ok=True)
    with open("./asset_output/catalog.json", "w") as f:
        catalog = get_catalog()
        json.dump(catalog, f)
