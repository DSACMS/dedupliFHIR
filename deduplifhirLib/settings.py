from splink.duckdb.linker import DuckDBLinker
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on
from splink.datasets import splink_datasets

DEDUPE_VARS = [
    {"field": "family_name", "type": "String"},
    {"field": "family_name", "type": "Exact"},
    {"field": "given_name", "type": "String"},
    {"field": "gender", "type": "String"},
    {"field": "gender", "type": "Exact"},
    {"field": "birth_date", "type": "ShortString"},
    {"field": "phone", "type": "ShortString"},
    {"field": "street_address", "type": "String", "has_missing": True},
    {"field": "city", "type": "String"},
    {"field": "state", "type": "ShortString"},
    {"field": "postal_code", "type": "ShortString"},
]


df = splink_datasets.fake_1000

settings = {
    "link_type": "dedupe_only",
    "blocking_rules_to_generate_predictions": [
        block_on("first_name"),
        block_on("surname"),
    ],
    "comparisons": [
        ctl.name_comparison("first_name"),
        ctl.name_comparison("surname"),
        ctl.date_comparison("dob", cast_strings_to_date=True),
        cl.exact_match("city", term_frequency_adjustments=True),
        ctl.email_comparison("email", include_username_fuzzy_level=False),
    ],
}

if __name__ == "__main__":
    #DuckDBLinker just defines the Pandas Dataframe format as using
    #DuckDB style formatting
    linker = DuckDBLinker(df, settings)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)
    
    blocking_rule_for_training = block_on(["first_name", "surname"])
    
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    blocking_rule_for_training = block_on("substr(dob, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    
    pairwise_predictions = linker.predict()
    
    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)
    
    print(clusters.as_pandas_dataframe(limit=25))