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
  RESULTS_SPREADSHEET: "deduped_record_mapping.xlsx",
};

module.exports = constants;
