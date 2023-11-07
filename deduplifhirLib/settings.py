from splink.datasets import splink_datasets
from splink.duckdb.linker import DuckDBLinker
import altair as alt

import pandas as pd 
pd.options.display.max_rows = 1000
df = splink_datasets.historical_50k

from splink.duckdb.blocking_rule_library import block_on

# Simple settings dictionary will be used for exploratory analysis
settings = {
    "link_type": "dedupe_only",
    "blocking_rules_to_generate_predictions": [
        block_on(["first_name", "surname"]),
        block_on(["surname", "dob"]),
        block_on(["first_name", "dob"]),
        block_on(["postcode_fake", "first_name"]),
    ],
}
linker = DuckDBLinker(df, settings)

linker.profile_columns(
    ["first_name", "postcode_fake", "substr(dob, 1,4)"], top_n=10, bottom_n=5
)