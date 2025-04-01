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
import sys

import boto3
import requests
from convert_formats import (
    convert_request_to_physrisk_format,
    convert_response_from_physrisk_format,
)
from physrisk.container import Container

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
    parser.add_argument("--assets", type=str, help="Geojson of the assets")
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
        "id": "",
        "type": "Catalog",
        "description": "OS-C physrisk asset vulnerability catalog",
        "links": [
            {"rel": "self", "href": "./catalog.json"},
            {"rel": "root", "href": "./catalog.json"},
        ],
    }


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
    with open(file_path, encoding="utf-8") as file:
        content = file.read()
        if not content.strip():
            raise RuntimeError(f"The JSON file {file_path} is empty.")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Failed to decode the content of the JSON file {file_path}"
            ) from exc


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
    url_response = requests.get(url, timeout=30)
    if url_response.status_code != 200:
        raise RuntimeError(
            f"Request to get the content of the input JSON {url} over "
            f"HTTP failed: {url_response.text}"
        )
    content = url_response.content.decode("utf-8")
    if not content.strip():
        raise RuntimeError(f"The JSON content from {url} is empty.")
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Failed to decode the content of the input JSON {url} over HTTP"
        ) from exc


def extract_bucket_and_key_from_s3_url(s3_path):
    """
    Extracts the bucket name and key from an S3 URL.

    Args:
        s3_path (str): The S3 URL in the format 's3://bucket_name/key'.

    Returns:
        tuple: A tuple containing the bucket name (str) and the key (str).
    """
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts.pop(0)
    key = "/".join(path_parts)
    return bucket, key


def load_json_from_s3(file_name):
    """
    Loads JSON content from an S3 path and returns it as a dictionary.

    Args:
        s3_path (str): The S3 path to the JSON file.

    Returns:
        dict: The JSON content as a dictionary.

    Raises:
        RuntimeError: If the file is empty or contains invalid JSON.
    """
    s3 = boto3.client("s3")
    bucket_name, key = extract_bucket_and_key_from_s3_url(file_name)
    logger.info(f"Downloading key: {key} from bucket: {bucket_name}...")
    local_file = os.path.basename(key)
    s3.download_file(bucket_name, key, local_file)
    return load_json_from_file(local_file)


if __name__ == "__main__":
    if not os.getenv("OSC_S3_ACCESS_KEY") or not os.getenv("OSC_S3_SECRET_KEY"):
        logger.error("AWS credentials not found")
        sys.exit(1)

    # Getting the json string
    args = parse_arguments()
    try:
        if args.assets.startswith("http://") or args.assets.startswith("https://"):
            logger.info("Getting the content of the input JSON over HTTP")
            request_params = load_json_from_url(args.assets)
        elif args.assets.startswith("s3://"):
            logger.info("Getting the content of the input JSON from S3")
            request_params = load_json_from_s3(args.assets)
        else:
            logger.info("Reading the input JSON file from S3")
            s3_url = f"s3://workspaces-eodhp-test/{args.assets}"
            request_params = load_json_from_s3(s3_url)
    except RuntimeError as e:
        logger.error(e)
        sys.exit(1)

    request_pr_format = convert_request_to_physrisk_format(json_in=request_params)
    response = make_request(params=request_pr_format)
    try:
        response_json = json.loads(response)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Failed to decode the response JSON") from exc
    updated_geojson = convert_response_from_physrisk_format(
        json_in=response_json, original_geojson=request_params
    )

    # Make a stac catalog.json file to satitsfy the process runner
    with open("./catalog.json", "w", encoding="utf-8") as f:
        catalog = get_catalog()
        catalog["data"] = updated_geojson
        json.dump(catalog, f)
