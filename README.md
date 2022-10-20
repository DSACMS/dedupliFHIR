<!--- # NOTE: Modify sections marked with `TODO` and then rename the file.-->

# eCQM Dedupe

 Prototype for basic deduplication and aggregation of eCQM data 

### Agency Mission

### Team Mission

### Project Vision

### Project Information
<!-- Example Innersource Project Info
 * [Project Website](https://cms.gov/digital-service-cms)
 * [Project Documentation:](https://confluence.cms.gov/)
 * [Project Sprint/Roadmap:](https://jira.cms.gov/)
 * [Project Slack Channel:](https://cmsgov.slack.com/archives/XXXXXXXXXX)
 * [Project Tools/Hosting/Deployment:](https://confluence.cms.gov)
 * Project Keyword(s) for Search: KEYWORD1, KEYWORD2
 * Project Members:
    * Team Lead, PO, Delivery Lead, Approvers, Trusted Committers etc.
-->

<!-- Example Open Source Info
 * [Project Website](https://cms.gov/digital-service-cms)
 * [Project Documentation:](https://confluence.cms.gov/)
 * Public Contact: opensource@cms.hhs.gov (**NOTE: Do not use individual/personal email addresses**)
 * Follow [@CMSgov](https://twitter.com/cmsgov) on Twitter for updates.
-->

### Installation

```
make install
```

## Setup

Add FHIR JSON bundle files to `input/patients.json` and `input/measures.json` and then run:

```
make all
```

You'll be prompted to train the deduplication model using the CLI for [`csvdedupe`](https://github.com/dedupeio/csvdedupe)

### Details

- Add files to `input/patients.json` and `input/measures.json`
- Convert Patient FHIR JSON bundle to CSV of relevant fields
- Run `csvdedupe` on Patient CSV
- Group `csvdedupe` output into a mapping of IDs that need to be converted
- Drop patients with IDs in `from` column from FHIR JSON bundle
- Convert all IDs in FHIR measure bundle that are in `from` column to `to` value
- Run `fqm-execution` calculations on cleaned bundles

## TODO:

- Figure out schema used for patient and measure/valueset bundles
- [Patient/measure exammple?](https://github.com/projecttacoma/fqm-execution/blob/3767d19700a48baa1609257033e4179eea485aba/test/fixtures/elm/CMS13v2.json)
- [Patient bundle example](https://github.com/projecttacoma/fqm-execution/blob/4738f84b72290c2d715c902163043674213fe837/test/fixtures/EXM111-9.1.000/Armando772_Almanza534_08fc9439-b7ff-4309-b409-4d143388594c.json)

## Questions

- Are measures just instructions and patient bundles contain actual information?
  - If so, should run everything on patient bundle
- Should we pre-generate weights rather than training?

## References

- http://hl7.org/fhir/us/identity-matching/2022May/
- [Northwestern notes](https://docs.google.com/document/d/1sQPz6golYBLg3KIFmAUGzkxc7IQVFHacP1pBxQecO8M/edit#heading=h.wpfu2n41bod5)

## Contributing

Thank you for considering contributing to an Open Source project of the US
Government! For more information about our contribution guidelines, see
[CONTRIBUTING.md](CONTRIBUTING.md)

## Security

For more information about our Security, Vulnerability, and Responsible
Disclosure Policies, see [SECURITY.md](SECURITY.md).

## Authors and Maintainers

For more information about our Authors and maintainers, see [MAINTAINERS.md](MAINTAINERS.md).
A full list of contributors can be found on [https://github.cms.gov/$USERNAME/$REPONAME/graphs/contributors](https://github.cms.gov/$USERNAME/$REPONAME/graphs/contributors).

## Public domain

This project is licensed within in the public domain within the United States,
and copyright and related rights in the work worldwide are waived through the
[CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0 dedication. By
submitting a pull request or issue, you are agreeing to comply with this waiver
of copyright interest.
