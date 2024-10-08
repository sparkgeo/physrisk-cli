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
import tempfile

import boto3
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


def download_file(s3_link: str, temp_file: str):
    """
    Downloads a file from an S3 bucket.

    This function downloads a file from an S3 bucket using the provided link and
    saves it to the specified location.

    Args:
    - s3_link (str): The link to the file in the S3 bucket.
    - temp_file (str): The path to save the downloaded file.
    """

    s3 = boto3.client("s3")
    print("Downloading file from S3...")
    s3_bucket = s3_link.split("/")[2]
    s3_bucketkey = "/".join(s3_link.split("/")[3:])
    s3.download_file(s3_bucket, s3_bucketkey, temp_file)


def load_json_from_file(file_path):
    """
    Loads JSON content from a file and returns it as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The JSON content as a dictionary.

    Raises:
        RuntimeError: If the file is empty or contains invalid JSON.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        if not content.strip():
            raise RuntimeError(f"The JSON file {file_path} is empty.")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(
                f"Failed to decode the content of the JSON file {file_path}"
            )


def load_json_from_url(url):
    """
    Loads JSON content from a URL and returns it as a dictionary.

    Args:
        url (str): The URL to the JSON file.

    Returns:
        dict: The JSON content as a dictionary.

    Raises:
        RuntimeError: If the request fails or the content is invalid JSON.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(
            f"Request to get the content of the input JSON {url} over HTTP failed: {response.text}"
        )
    content = response.content.decode("utf-8")
    if not content.strip():
        raise RuntimeError(f"The JSON content from {url} is empty.")
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"Failed to decode the content of the input JSON {url} over HTTP"
        )


def load_json_from_s3(s3_path):
    """
    Loads JSON content from an S3 path and returns it as a dictionary.

    Args:
        s3_path (str): The S3 path to the JSON file.

    Returns:
        dict: The JSON content as a dictionary.

    Raises:
        RuntimeError: If the file is empty or contains invalid JSON.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False).name
    download_file(s3_path, temp_file)
    return load_json_from_file(temp_file)


if __name__ == "__main__":
    if not os.getenv("OSC_S3_ACCESS_KEY") or not os.getenv("OSC_S3_SECRET_KEY"):
        logger.error("AWS credentials not found")
        sys.exit(1)

    # Getting the json string
    args = parse_arguments()
    try:
        if "http" in args.json_file:
            logger.info("Getting the content of the input JSON over HTTP")
            request_params = load_json_from_url(args.json_file)
        elif "s3" in args.json_file:
            logger.info("Getting the content of the input JSON from S3")
            request_params = load_json_from_s3(args.json_file)
        else:
            logger.info("Reading the input JSON file")
            request_params = load_json_from_file(args.json_file)
    except RuntimeError as e:
        logger.error(e)
        sys.exit(1)

    request_pr_format = convert_request_to_physrisk_format(json_in=request_params)
    response = make_request(params=request_pr_format)
    try:
        response_json = json.loads(response)
    except json.JSONDecodeError:
        raise RuntimeError("Failed to decode the response JSON")
    updated_geojson = convert_response_from_physrisk_format(
        json_in=response_json, original_geojson=request_params
    )

    # Make a stac catalog.json file to satitsfy the process runner
    os.makedirs("asset_output", exist_ok=True)
    with open("./asset_output/catalog.json", "w", encoding="utf-8") as f:
        catalog = get_catalog()
        catalog["data"] = updated_geojson
        json.dump(catalog, f)
