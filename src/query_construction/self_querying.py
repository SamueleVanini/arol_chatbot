from langchain.chains.query_constructor.schema import AttributeInfo

# TODO: check if we should use space or underscore for the name of the Attribute (e.g. bottles per hour vs. bottles_per_hour)

# Info about the metadata associated with each document in the vectorstore, it is used as a context for the llm in self-querying
# NOTE: Expected metadata value to be a str, int, float or bool. Otherwise Chroma will raise a ValueError exception
METADATA_FIELD_INFO = [
    AttributeInfo(
        name="name",
        description="The name of the machine",
        type="string",
    ),
    AttributeInfo(
        name="bottles_per_hour",
        description="The number of closed bottles every hour",
        type="integer",
    ),
    AttributeInfo(
        name="bottles_per_minute",
        description="The number of closed bottles every minute",
        type="integer",
    ),
    AttributeInfo(
        name="caps_per_hour",
        description="The number of closed caps every hour",
        type="integer",
    ),
    AttributeInfo(
        name="caps_per_minute",
        description="The number of closed caps every minute",
        type="integer",
    ),
    # try to concatenate caps application values in a single string a use the "like" comparison statement duriong self querying
    # AttributeInfo(name="caps application", description="The type of caps usable by the machine", type="string"),
]

DOCUMENT_CONTENT_DESCRIPTION = "Small paragraph contaning all the machine's information and statistics"


def metadata_extraction(record: dict, metadata: dict) -> dict:

    metadata["name"] = record.get("name")
    speed_production = record.get("main_features").get("speed production")[0]

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

    return metadata
