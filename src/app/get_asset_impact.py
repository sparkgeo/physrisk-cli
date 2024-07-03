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
    parser.add_argument("--json_string", type=str, help="Geojson of the assets")
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


def split_into_batches(lst, batch_size):
    """
    Splits a list into smaller lists (batches) of a specified size.

    Parameters:
    - lst (list): The list to be split into batches.
    - batch_size (int): The size of each batch.

    Yields:
    - list: A batch of the original list, with length up to `batch_size`.
    """
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]


def prepare_batches(feature_batches, original_geojson):
    """
    This function takes a list of feature batches and the original GeoJSON, and
    for each batch, it creates a new GeoJSON object that retains the original
    structure but contains only the features from the current batch.

    Parameters:
    - batches (list of list): A list of batches, where each batch is a list of
    GeoJSON features.
    - original_geojson (dict): The original GeoJSON object.

    Returns:
    - list of dict: A list of new GeoJSON objects, each containing a batch of features.
    """
    batched_geojsons = []
    for feature_batch in feature_batches:
        new_geojson = original_geojson.copy()  # Copy the original GeoJSON structure
        new_geojson["features"] = feature_batch  # Replace features with the batch
        batched_geojsons.append(new_geojson)
    return batched_geojsons


def batch_up(geojson_request, batch_size):
    """
    This function is a high-level utility that combines splitting the GeoJSON features
    into batches and then preparing new GeoJSON objects for each batch.
    It is intended to be used when the features of a GeoJSON need to be processed in
    smaller groups while retaining the original GeoJSON structure.

    Parameters:
    - geojson_request (dict): The GeoJSON object to be batched.
    - batch_size (int): The size of each batch.

    Returns:
    - list of dict: A list of new GeoJSON objects, each containing a batch of features.
    """
    logger.info("Batching up the GeoJSON request")
    batched_features = list(split_into_batches(geojson_request["features"], batch_size))
    batched_geojsons = prepare_batches(batched_features, geojson_request)
    return batched_geojsons


if __name__ == "__main__":
    if not os.getenv("OSC_S3_ACCESS_KEY") or not os.getenv("OSC_S3_SECRET_KEY"):
        logger.error("AWS credentials not found")
        sys.exit(1)

    # Getting the json string
    args = parse_arguments()
    request_params = json.loads(args.json_string)

    # Split the request into batches of 80 of features each
    batches = batch_up(request_params, 80)

    response_geojson = {
        "type": "FeatureCollection",
        "features": [],
        "properties": request_params["properties"],
    }
    for batch_no, batch in enumerate(batches):
        logger.info(f"Processing batch {batch_no} of {len(batch['features'])}")
        request_pr_format = convert_request_to_physrisk_format(batch)
        response = make_request(request_pr_format)
        response_json = json.loads(response)
        updated_geosjon = convert_response_from_physrisk_format(response_json, batch)
        response_geojson["features"].extend(updated_geosjon["features"])

    # Make a stac catalog.json file to satitsfy the process runner
    os.makedirs("asset_output", exist_ok=True)
    with open("./asset_output/catalog.json", "w", encoding="utf-8") as f:
        catalog = get_catalog()
        catalog["data"] = response_geojson
        json.dump(catalog, f)
