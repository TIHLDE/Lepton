<br/>
<p align="center">
    <a href="https://tihlde.org" target="_blank">
        <img width="50%" src="https://i.ibb.co/6YpLt8m/TIHLDE-LOGO-BL.png" alt="TIHLDE logo">
    </a>
</p>


<h1 align="center">Lepton</h1>

<h4 align="center">
    Open source backend for <a href="https://tihlde.org">TIHLDE's website.</a>
</h4>

<br/>

<p align="CENTER">
<a href="https://github.com/tihlde/Lepton/actions"><img alt="Actions Status" src="https://github.com/tihlde/Lepton/workflows/Test and linting/badge.svg?label=github-actions"></a>
<a href="https://github.com/psf/black/blob/master/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/tihlde/Lepton/commits/master" target="_blank">
    <img src="https://img.shields.io/github/commit-activity/y/tihlde/lepton.svg" alt="GitHub commit activity">
</a>
<a href="https://github.com/tihlde/lepton/graphs/contributors" target="_blank">
    <img src="https://img.shields.io/github/contributors-anon/tihlde/lepton.svg" alt="GitHub contributors">
</a>
</p>

<br/>
<p align="center">
    <img width="80%" src="https://i.ibb.co/CtHxCph/Skjermbilde-2020-10-31-224329.png" alt="TIHLDEs nettside">
</p>
<br/>


## 🚀 Getting started

Lepton requires Docker and Docker Compose.


```
# Setup a local repository
git clone https://github.com/tihlde/Lepton.git
cd Lepton

# If this is your first time running the application
make fresh

# Thats it!
```

From now on it's enough to run `make start` to run the application.

We use [GNU Make](https://www.gnu.org/software/make/) to simplify common commands.
Have a look at the `makefile` to find out more about how to run the project without it.


#### ⚙ Configuration
No configuration is required to get started, but if you would like to
configure further or override existing ones, put the following environment variables
in a _.env_ file in the repository root.

```
# Database connection variables
DATABASE_HOST= HOST_URL
DATABASE_NAME= DATABASE_NAME
DATABASE_PASSWORD= PASSWORD
DATABASE_PORT= PORT (normally 3306)
DATABASE_USER= USERNAME

# Optional for using mailing
EMAIL_HOST= HOST_URL
EMAIL_PORT= PORT (normally 587)
EMAIL_USER= EMAIL_USER
EMAIL_PASSWORD= EMAIL_PASSWORD

# Optional for uploading files to Azure
AZURE_STORAGE_CONNECTION_STRING= CONNECTION_STRING
```

## ✅ Test the application
The tests can be run with pytest by running `make test`.

To run with test coverage, run `make test args="--cov"`.

## ❤ Contributing
The Lepton backend is an open source project built on voluntary work.
We are committed to a fully transparent development process, and highly appreciate any contributions.
Whether you are helping us by fixing bugs, proposing new feature, improving our documentation,
or simply spreading the word - **we would love to have you as part of our community**.

## 🤝  Found a bug? Missing a specific feature?
Feel free to file a new issue with a respective title and description
in the [TIHLDE/Lepton](https://github.com/TIHLDE/Lepton/issues) repository.
If you have already found a solution to your problem, we would love to review your pull request!
We enforce the PEP-8 style guide with isort, black and flake8.
Have a look at `setup.cfg` to find out more about our coding standards.

## 📫 Contact
Feel free to send us a message on our official [slack channel](https://tihlde.slack.com/archives/C01CJ0EQCFM), or email us at index@tihlde.org.

## 📘 License
The code in this repository is licensed under the [MIT license](LICENSE.md).
