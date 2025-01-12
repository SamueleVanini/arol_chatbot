from langchain.chains.query_constructor.schema import AttributeInfo

# TODO: check if we should use space or underscore for the name of the Attribute (e.g. bottles per hour vs. bottles_per_hour)

# Info about the metadata associated with each document in the vectorstore, it is used as a context for the llm in self-querying
# NOTE: Expected metadata value to be a str, int, float or bool. Otherwise Chroma will raise a ValueError exception
METADATA_FIELD_INFO = [
    AttributeInfo(
        name="name",
        description="The name of the machine. The field MUST be user in lower case form",
        type="string",
    ),
    AttributeInfo(
        name="bottles_per_hour",
        description="The number of closed bottles every hour. The field MUST be user in lower case form",
        type="integer",
    ),
    AttributeInfo(
        name="bottles_per_minute",
        description="The number of closed bottles every minute. The field MUST be user in lower case form",
        type="integer",
    ),
    AttributeInfo(
        name="caps_per_hour",
        description="The number of closed caps every hour. The field MUST be user in lower case form",
        type="integer",
    ),
    AttributeInfo(
        name="caps_per_minute",
        description="The number of closed caps every minute. The field MUST be user in lower case form",
        type="integer",
    ),
    # try to concatenate caps application values in a single string a use the "like" comparison statement duriong self querying
    # AttributeInfo(name="caps application", description="The type of caps usable by the machine", type="string"),
]


def get_metadata_field_info(machines_name: list[str]):
    return [
        AttributeInfo(
            name="name",
            description=f"The name of the machine. The field MUST be used in lower case form. Choose only from the following list: {machines_name}. If other machine are named DO NOT add a condition for the name in the filter",
            type="string",
        ),
        AttributeInfo(
            name="bottles_per_hour",
            description="The number of closed bottles every hour. The field MUST be used in lower case form",
            type="integer",
        ),
        AttributeInfo(
            name="bottles_per_minute",
            description="The number of closed bottles every minute. The field MUST be used in lower case form",
            type="integer",
        ),
        AttributeInfo(
            name="caps_per_hour",
            description="The number of closed caps every hour. The field MUST be used in lower case form",
            type="integer",
        ),
        AttributeInfo(
            name="caps_per_minute",
            description="The number of closed caps every minute. The field MUST be used in lower case form",
            type="integer",
        ),
        AttributeInfo(
            name="beverage",
            description=f"A flag to indicate if the machine works in the beverage industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="food",
            description=f"Flag to indicate if the machine works in the food industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="chemical",
            description=f"Flag to indicate if the machine works in the chemical industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="pharmaceutical",
            description=f"Flag to indicate if the machine works in the pharmaceutical industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="spirits",
            description=f"Flag to indicate if the machine works in the spirits industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="personal care",
            description=f"Flag to indicate if the machine works in the personal care industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="home care",
            description=f"Flag to indicate if the machine works in the home care industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="wine",
            description=f"Flag to indicate if the machine works in the wine industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="beer",
            description=f"Flag to indicate if the machine works in the beer industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="champagne",
            description=f"Flag to indicate if the machine works in the champagne industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="champagne",
            description=f"Flag to indicate if the machine works in the champagne industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        AttributeInfo(
            name="houseold care",
            description=f"Flag to indicate if the machine works in the houseold care industry. The field MUST be used in lower case form. The flag is not mutual exclusive with others flags. Use this flag only if its value in the filter is equal to true.",
            type="bool",
        ),
        # AttributeInfo(
        #     name="markets",
        #     description=f"markets in which the machine can operate. The field MUST be used in lower case form. Choose one or more values only from the following list: {markets}. If other markets are named DO NOT add a condition for the name in the filter",
        #     type="string or list[string]",
        # ),
        # try to concatenate caps application values in a single string a use the "like" comparison statement duriong self querying
        # AttributeInfo(name="caps application", description="The type of caps usable by the machine", type="string"),
    ]


# DOCUMENT_CONTENT_DESCRIPTION = "Small paragraph contaning all the machine's information and statistics"
DOCUMENT_CONTENT_DESCRIPTION = "small json object with machine's information and statistics. Each machine have multiple flag that are NOT mutually exclusive. Don't add in the filter flags that are not mentioned."


def metadata_extraction(record: dict, metadata: dict) -> dict:

    metadata["name"] = record.get("name")
    speed_production = record.get("main_features").get("speed production")[0]
    markets: list[str] = record.get("main_features").get("main market")

    prod_speed_py_int_number = speed_production.replace(".", "_")

    top_type_hour = "bottles_per_hour"
    top_type_minute = "bottles_per_minute"

    if "cpm" in prod_speed_py_int_number:
        top_type_hour = "caps_per_hour"
        top_type_minute = "caps_per_minute"

    # really ugly name but quite fitting (we are replacing the "." used to represent number in the Arol Catalog with "_")
    minutes_split, hours_split = prod_speed_py_int_number.split("/")
    for word in minutes_split.split(" "):
        if "_" in word or word.isnumeric():
            metadata[top_type_minute] = int(word)

    for word in hours_split.split(" "):
        if "_" in word or word.isnumeric():
            metadata[top_type_hour] = int(word)

    for market in markets:
        if market.startswith("wine"):
            and_splits = market.split("&")
            if len(and_splits) == 1:
                metadata["wine"] = True
            else:
                for split in and_splits:
                    metadata[split] = True
        else:
            metadata[market] = True

    return metadata
