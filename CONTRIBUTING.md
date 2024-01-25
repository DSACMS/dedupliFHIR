<!--- # NOTE: Modify sections marked with `TODO` and then rename the file.-->

# How to Contribute

We're so thankful you're considering contributing to an [open source project of
the U.S. government](https://code.gov/)! If you're unsure about anything, just
ask -- or submit the issue or pull request anyway. The worst that can happen is
you'll be politely asked to change something. We appreciate all friendly
contributions.

We encourage you to read this project's CONTRIBUTING policy (you are here), its
[LICENSE](LICENSE.md), and its [README](README.md).

## Getting Started
<!--- ### TODO: If you have 'good-first-issue' or 'easy' labels for newcomers, mention them here.-->
First, please install poetry (see [installation instructions](https://python-poetry.org/docs/#installation)).

Then, install Python dependencies with
```
make install
```

To run our Python tests run
```
make test
```

To Access the Python CLI immediately use
```
poetry run python cli/ecqm-dedupe.py <command> [--fmt] [<args>]
``` 


### Team Specific Guidelines

- Please try to keep PRs to a reasonable size; try to split large contributions to multiple PRs
- Please create Pull Requests into dev unless the contribution is some kind of bugfix or urgent hotfix.
- Document and explain the contribution clearly according to provided standards when possible
- Feel free to reach out to us if there is any confusion

### Building the Project

<!--- ### TODO -->
Poetry is required to build dependencies (see [instructions](https://python-poetry.org/docs/#installation)).

Then, install Python dependencies with
```
make install
```

<!--- ### TODO -->

### Workflow and Branching

We follow the [GitHub Flow Workflow](https://guides.github.com/introduction/flow/)

1.  Fork the project 
2.  Check out the `main` branch 
3.  Create a feature branch
4.  Write code and tests for your change 
5.  From your branch, make a pull request against `dev` if you have a feature change and `main` if it is a hotfix 
6.  Work with repo maintainers to get your change reviewed and resolve git history if needed
7.  Wait for your change to be pulled into `dev` and later released into `main`
8.  Delete your feature branch

### Testing Conventions

<!--- TODO -->
This project uses pytest as the main testing framework for the project's cli. 

Python tests can be found in the `cli/deduplifhirLib/tests.py`. Any new testing
contributions are greatly appreciated and needed to ensure quality of any interpreted
language project. 

### Coding Style and Linters

<!--- TODO: Code Style Guide 

1. Mention any style guides you adhere to (e.g. pep8, etc...)
1. Mention any linters your project uses (e.g. flake8, jslint, etc...) 
1. Mention any naming conventions your project uses (e.g. Semantic Versioning, CamelCasing, etc...)
1. Mention any other content guidelines the project adheres to (e.g. plainlanguage.gov, etc...)

-->
This project adheres to PEP8 rules and guidelines whenever possible when accepting
new contributions of Python code. Although, there are good reasons to ignore particular guidelines
in particular situations. Further information on PEP8 can be found [here.](https://peps.python.org/pep-0008/)

This project also uses pylint as the main linter for the moment and employs pylint checks upon new pull
requests into protected branches. Python code quality checks are extremely useful for lowering the
cost of maintenence of Python projects. Further information on Pylint can be found [here.](https://pylint.readthedocs.io/en/latest/)

### Issues

When creating an issue please try to adhere to the following format:

    module-name: One line summary of the issue (less than 72 characters)

    ### Expected behavior

    As concisely as possible, describe the expected behavior.

    ### Actual behavior

    As concisely as possible, describe the observed behavior.

    ### Steps to reproduce the behavior

    List all relevant steps to reproduce the observed behavior.

### Pull Requests

Comments should be formatted to a width no greater than 80 columns.

Files should be exempt of trailing spaces.

We adhere to a specific format for commit messages. Please write your commit
messages along these guidelines. Please keep the line width no greater than 80
columns (You can use `fmt -n -p -w 80` to accomplish this).

    module-name: One line description of your change (less than 72 characters)

    Problem

    Explain the context and why you're making that change.  What is the problem
    you're trying to solve? In some cases there is not a problem and this can be
    thought of being the motivation for your change.

    Solution

    Describe the modifications you've done.

    Result

    What will change as a result of your pull request? Note that sometimes this
    section is unnecessary because it is self-explanatory based on the solution.

Some important notes regarding the summary line:

* Describe what was done; not the result 
* Use the active voice 
* Use the present tense 
* Capitalize properly 
* Do not end in a period — this is a title/subject 
* Prefix the subject with its scope

## Code Review

The repository on GitHub is kept in sync with an internal repository at
github.cms.gov. For the most part this process should be transparent to the
project users, but it does have some implications for how pull requests are
merged into the codebase.

When you submit a pull request on GitHub, it will be reviewed by the project
community (both inside and outside of github.cms.gov), and once the changes are
approved, your commits will be brought into github.cms.gov's internal system for
additional testing. Once the changes are merged internally, they will be pushed
back to GitHub with the next sync.

This process means that the pull request will not be merged in the usual way.
Instead a member of the project team will post a message in the pull request
thread when your changes have made their way back to GitHub, and the pull
request will be closed.

The changes in the pull request will be collapsed into a single commit, but the
authorship metadata will be preserved.

## Documentation

We also welcome improvements to the project documentation or to the existing
docs. Please file an [issue](https://github.com/cmsgov/cmsgov-example-repo/issues).

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

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request or issue, you are agreeing to comply with this waiver of copyright interest.
