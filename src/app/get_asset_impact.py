#! /usr/local/bin/python

"""
This module is used to make a request to get hazard data. It includes functions
to parse command-line arguments and make the request.
The module uses the Container from the physrisk package to make the request.
"""

import argparse
import json
import os
import sys

import requests
from convert_formats import (
    convert_request_to_physrisk_format,
    convert_response_from_physrisk_format,
)
from physrisk.container import Container
from physrisk_cli_logger import logger


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
    logger.info("Making request to get asset impact")
    try:
        requester = Container.requester
        request_id = "get_asset_impact"
        params["group_ids"] = ["osc"]
        logger.debug("Request ID: %s", request_id)
        logger.debug("Request params: %s", params)
        return requester().get(request_id=request_id, request_dict=params)
    except Exception:
        logger.exception("Error in making request")
        return None


def parse_arguments():
    """
    Parses command-line arguments for the request.

    Returns:
        argparse.Namespace: An object that holds the parsed arguments as
        attributes.
    """
    logger.info("Parsing command-line arguments")
    parser = argparse.ArgumentParser(description="Make a request.")
    # parser.add_argument("--json", type=str, help="JSON string with request parameters")
    parser.add_argument("--json_file", type=str, help="Geojson of the assets")
    parser.add_argument(
        "--flat",
        action="store_true",
        default=True,
        help="Optional argument to flatten the JSON output",
    )
    return parser.parse_args()


def get_catalog() -> dict:
    """
    Creates and returns a basic STAC catalog dictionary.

    This function generates a dictionary representing a SpatioTemporal Asset Catalog
    (STAC) catalog with predefined properties.

    Returns:
    - dict: A dictionary representing the STAC catalog with predefined properties.
    """
    logger.info("Creating STAC catalog")
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
        logger.error("AWS credentials not found")
        sys.exit(1)

    # Getting the json string
    args = parse_arguments()
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

    request_pr_format = convert_request_to_physrisk_format(json_in=request_params)
    response = make_request(params=request_pr_format)
    response_json = json.loads(response)
    updated_geojson = convert_response_from_physrisk_format(
        json_in=response_json, original_geojson=request_params
    )

    # Make a stac catalog.json file to satitsfy the process runner
    os.makedirs("asset_output", exist_ok=True)
    with open("./asset_output/catalog.json", "w", encoding="utf-8") as f:
        catalog = get_catalog()
        catalog["data"] = updated_geojson
        json.dump(catalog, f)
