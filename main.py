import argparse
import logging
import os

from dotenv import load_dotenv
from physrisk.container import Container

logging.basicConfig(level=logging.INFO)


def make_request(request_params):
    """
    Makes a request to get hazard data.

    This function creates a request dictionary with the provided parameters,
    then uses the requester from the Container to make the request. If an error
    occurs during the request, it is logged and the function returns None.

    Args:
        request_params (dict): The parameters for the request. These will be
            included in the 'items' list of the request dictionary.

    Returns:
        dict: The response from the request, or None if an error occurred.
    """
    try:
        requester = Container.requester
        request_id = "get_hazard_data"
        request_dict = {
            "group_ids": ["osc"],
            "items": [request_params],
        }
        return requester().get(request_id=request_id, request_dict=request_dict)
    except Exception as e:
        logging.error("Error in making request: %s", e)
        return None


def parse_arguments():
    """
    Parses command-line arguments for the request.

    This function uses argparse to parse command-line arguments. The arguments
    include various parameters for the request, such as the request item ID,
    year, scenario, indicator ID, event type, longitudes, and latitudes.

    Returns:
        argparse.Namespace: An object that holds the parsed arguments as attributes.
    """
    parser = argparse.ArgumentParser(description="Make a request.")
    parser.add_argument("--request_item_id", type=str, default="Test")
    parser.add_argument("--year", type=int, default=2050)
    parser.add_argument("--scenario", type=str, default="ssp585")
    parser.add_argument("--indicator_id", type=str, default="mean_work_loss/high")
    parser.add_argument("--event_type", type=str, default="ChronicHeat")
    parser.add_argument(
        "--longitudes", nargs="+", type=float, default=[69.4787, 68.71, 20.1047]
    )
    parser.add_argument(
        "--latitudes", nargs="+", type=float, default=[34.556, 35.9416, 39.9116]
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Check if .env file exists before loading
    if os.path.exists(".env"):
        load_dotenv()
    else:
        logging.warning("No .env file found")
    if not os.getenv("OSC_S3_ACCESS_KEY" or not os.getenv("OSC_S3_SECRET_KEY")):
        logging.error("AWS credentials not found")
        exit(1)
    args = parse_arguments()
    request_params = vars(args)
    response = make_request(request_params)
    if response is not None:
        print(response)
    else:
        logging.error("Request failed")
