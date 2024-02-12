# CHANGELOG.md

## Version 1 

Features:

  - Created flask frontend for dedupliFHIR interface
  - Users used frontend to supply training data as well as show duplicates
  - Use dedupe python library on the backend to deduplicate data


## Version 2

### Pre-Alpha

Features:
  - Rewrite backend with Splink data deduplication library
  - Use Click to create our CLI
  - Use Faker to generate test data
  - Work Started on Electron front-end to replace flask front-end
  - Create GitHub CI/CD action workflow for the repo