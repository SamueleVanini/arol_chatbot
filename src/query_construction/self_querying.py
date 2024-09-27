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
    # AttributeInfo(name="caps application", description="The type of caps usable by the machine", type="string"),
]

DOCUMENT_CONTENT_DESCRIPTION = "Json object describing the capping machine"

# TODO: parse production speed to extract bottles per hour and minute
# TODO: text the metadata_extraction function


def metadata_extraction(record: dict, metadata: dict) -> dict:

    metadata["name"] = record.get("name")
    main_features = record.get("main_features")

    for prod_speed_str in main_features.get("speed production"):
        # really ugly name but quite fitting (we are replacing the "." used to represent number in the Arol Catalog with "_")
        prod_speed_py_int_number = prod_speed_str.replace(".", "_")
        minutes_split, hours_split = prod_speed_py_int_number.split("/")
        for word in minutes_split.split(" "):
            if "_" in word or word.isnumeric():
                metadata["bottles_per_minute"] = int(word)

        for word in hours_split.split(" "):
            if "_" in word or word.isnumeric():
                metadata["bottles_per_hour"] = int(word)

    return metadata
