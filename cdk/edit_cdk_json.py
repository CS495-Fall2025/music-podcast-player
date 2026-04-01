import json
import os
from pathlib import Path


QUALIFIERS_BY_ENV = {
    "development": "dev",
    "production": "prod",
}
QUALIFIER_KEY = ["context", "@aws-cdk/core:bootstrapQualifier"]
PATH = Path(__file__).parent / "cdk.json"


def main() -> None:
    with open(PATH, "r") as file:
        data = json.load(file)

    relevant_dict = data
    for key in QUALIFIER_KEY[:-1]:
        relevant_dict = relevant_dict[key]

    qualifier = QUALIFIERS_BY_ENV[os.environ["DEPLOY_ENVIRONMENT"]]

    relevant_dict[QUALIFIER_KEY[-1]] = qualifier

    with open(PATH, "w") as file:
        json.dump(data, file, indent=2)


if __name__ == "__main__":
    main()
