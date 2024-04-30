import argparse

from dotenv import load_dotenv
from physrisk.container import Container

load_dotenv()



def make_request(request_params):
    requester = Container.requester
    request_id = "get_hazard_data"
    request_dict = {
        "group_ids": ["osc"],
        "items": [
            request_params
        ],
    }
    return requester().get(request_id=request_id, request_dict=request_dict)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Make a request.')
    parser.add_argument('--request_item_id', type=str, default="Test")
    parser.add_argument('--year', type=int, default=2050)
    parser.add_argument('--scenario', type=str, default="ssp585")
    parser.add_argument('--indicator_id', type=str, default="mean_work_loss/high")
    parser.add_argument('--event_type', type=str, default="ChronicHeat")
    parser.add_argument('--longitudes', nargs='+', type=float, default=[69.4787, 68.71, 20.1047])
    parser.add_argument('--latitudes', nargs='+', type=float, default=[34.556, 35.9416, 39.9116])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    request_params = vars(args)
    response = make_request(request_params)
    print(response)