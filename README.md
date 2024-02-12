<!--- # NOTE: Modify sections marked with `TODO` and then rename the file.-->

# eCQM Dedupe

A CLI bundled with an electron front-end that provides data-linkage and AI deduplication for reported
ACO data at scale.

## About the Project
As part of the Affordable Care Act, and attempts to reduce costs/utilization/expenditures, ACOS were created; Accountable care organizations.

Currently, ACO health metrics are self-reported and can result in duplicate records. This tool seeks
to leverage existing open source AI data linkage technology to help increase the quality of reported 
health data.

This tool was made to target the FHIR (and later QRDA) file formats of ACO reported health metrics.

This project originated from the CMS Open Source Community as a resource ACOs can use when preparing their patient records submission.


### Installation

You'll need poetry installed (see [installation instructions](https://python-poetry.org/docs/#installation)).

```
make install
```


To test your installation run:
```
make test
```

To run the cli (for now) use the command:
```
poetry run python cli/ecqm-dedupe.py <command> [--fmt] [<args>]
``` 
<!-- 
### TODO:

- Figure out schema used for patient and measure/valueset bundles
- [Patient/measure example?](https://github.com/projecttacoma/fqm-execution/blob/3767d19700a48baa1609257033e4179eea485aba/test/fixtures/elm/CMS13v2.json)
- [Patient bundle example](https://github.com/projecttacoma/fqm-execution/blob/4738f84b72290c2d715c902163043674213fe837/test/fixtures/EXM111-9.1.000/Armando772_Almanza534_08fc9439-b7ff-4309-b409-4d143388594c.json)
-->

### Questions

- Are measures just instructions and patient bundles contain actual information?
  - If so, should run everything on patient bundle
- Should we pre-generate weights rather than training?

### References

- http://hl7.org/fhir/us/identity-matching/2022May/

## Core Team
An up-to-date list of core team members can be found in [MAINTAINERS.md](MAINTAINERS.md). At this time, the project is still building the core team and defining roles and responsibilities. We are eagerly seeking individuals who would like to join the community and help us define and fill these roles.

## Documentation Index 
- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [MAINTAINERS.md](./MAINTAINERS.md)
- [CODEOWNERS.md](./CODEOWNERS.md)
- [GOVERNANCE.md](./GOVERNANCE.md)
- [COMMUNITY_GUIDELINES.md](./COMMUNITY_GUIDELINES.md)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [SECURITY.md](./SECURITY.md)
- [LICENSE](./LICENSE)

## Repository Structure

```
.
├── .github
│   └── workflows - Directory containing GitHub Actions workflows for automating CI/CD processes.
├── cli - Command line tool for data linkage and deduplication of ACO patient data.
│   └── deduplifhirLib
├── frontend - Native desktop app frontend built using Electron. 
└── profile - Information about the Digital Service at CMS team.
```


# Development and Software Delivery Lifecycle 
The following guide is for members of the project team who have access to the repository as well as code contributors. The main difference between internal and external contributions is that externabl contributors will need to fork the project and will not be able to merge their own pull requests. For more information on contribributing, see: [CONTRIBUTING.md](./CONTRIBUTING.md).

<!--- ## Local Development
<!--- # TODO - with example below:
This project is monorepo with several apps. Please see the [api](./api/README.md) and [frontend](./frontend/README.md) READMEs for information on spinning up those projects locally. Also see the project [documentation](./documentation) for more info.
-->

## Coding Style and Linters
Each application has its own linting and testing guidelines. Lint and code tests are run on each commit, so linters and tests should be run locally before committing.

## Branching Model
<!--- # TODO - with example below:
This project follows [trunk-based development](https://trunkbaseddevelopment.com/), which means:

* Make small changes in [short-lived feature branches](https://trunkbaseddevelopment.com/short-lived-feature-branches/) and merge to `main` frequently.
* Be open to submitting multiple small pull requests for a single ticket (i.e. reference the same ticket across multiple pull requests).
* Treat each change you merge to `main` as immediately deployable to production. Do not merge changes that depend on subsequent changes you plan to make, even if you plan to make those changes shortly.
* Ticket any unfinished or partially finished work.
* Tests should be written for changes introduced, and adhere to the text percentage threshold determined by the project.

This project uses **continuous deployment** using [Github Actions](https://github.com/features/actions) which is configured in the [./github/worfklows](.github/workflows) directory.

Pull-requests are merged to `main` and the changes are immediately deployed to the development environment. Releases are created to push changes to production.
-->

We follow the [GitHub Flow Workflow](https://guides.github.com/introduction/flow/)

1.  Fork the project 
2.  Check out the `main` branch 
3.  Create a feature branch
4.  Write code and tests for your change 
5.  From your branch, make a pull request against `dev` if you have a feature change and `main` if it is a hotfix 
6.  Work with repo maintainers to get your change reviewed and resolve git history if needed
7.  Wait for your change to be pulled into `dev` and later released into `main`
8.  Delete your feature branch

## Contributing
Thank you for considering contributing to an Open Source project of the US Government! For more information about our contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Codeowners
Those responsible for the code and documentation in this repository can be found in [CODEOWNERS.md](CODEOWNERS.md).

## Community
The DeDupliFHIR team is taking a community-first and open source approach to the product development of this tool. We believe government software should be made in the open and be built and licensed such that anyone can download the code, run it themselves without paying money to third parties or using proprietary software, and use it as they will.

We know that we can learn from a wide variety of communities, including those who will use or will be impacted by the tool, who are experts in technology, or who have experience with similar technologies deployed in other spaces. We are dedicated to creating forums for continuous conversation and feedback to help shape the design and development of the tool.

We also recognize capacity building as a key part of involving a diverse open source community. We are doing our best to use accessible language, provide technical and process documents, and offer support to community members with a wide variety of backgrounds and skillsets. 

### Community Guidelines
Principles and guidelines for participating in our open source community are can be found in [COMMUNITY_GUIDELINES.md](COMMUNITY_GUIDELINES.md). Please read them before joining or starting a conversation in this repo or one of the channels listed below. All community members and participants are expected to adhere to the community guidelines and code of conduct when participating in community spaces including: code repositories, communication channels and venues, and events. 

<!--
## Governance
Information about how the **{project_name}** community is governed may be found in [GOVERNANCE.md](GOVERNANCE.md).
-->

## Feedback
If you have ideas for how we can improve or add to our capacity building efforts and methods for welcoming people into our community, please let us know at **mailto:opensource@cms.hhs.gov**. If you would like to comment on the tool itself, please let us know by filing an **issue on our GitHub repository.**

<!--
## Glossary
Information about terminology and acronyms used in this documentation may be found in [GLOSSARY.md](GLOSSARY.md).
-->

## Policies

### Open Source Policy

We adhere to the [CMS Open Source
Policy](https://github.com/CMSGov/cms-open-source-policy). If you have any
questions, just [shoot us an email](mailto:opensource@cms.hhs.gov).

### Security and Responsible Disclosure Policy

*Submit a vulnerability:* Unfortunately, we cannot accept secure submissions via
email or via GitHub Issues. Please use our website to submit vulnerabilities at
[https://hhs.responsibledisclosure.com](https://hhs.responsibledisclosure.com).
HHS maintains an acknowledgements page to recognize your efforts on behalf of
the American public, but you are also welcome to submit anonymously.

For more information about our Security, Vulnerability, and Responsible Disclosure Policies, see [SECURITY.md](SECURITY.md).

## Public domain

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/) as indicated in our [LICENSE](LICENSE).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request or issue, you are agreeing to comply with this waiver of copyright interest.
