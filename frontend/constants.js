const constants = {
  SCRIPT: "ecqm_dedupe.py",
  COMMANDS: {
    DEDUPE_DATA: "dedupe-data",
  },
  OPTIONS: {
    FORMAT: "--fmt",
  },
  FORMAT: {
    CSV: "CSV",
    FHIR: "FHIR",
    TEST: "TEST",
  },
  RESULTS_FILE_NAME: "deduped_record_mapping",
};

module.exports = constants;
