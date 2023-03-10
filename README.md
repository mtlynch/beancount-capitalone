# beancount-capitalone

[![PyPI](https://img.shields.io/pypi/v/beancount-capitalone)](https://pypi.org/project/beancount-capitalone/)
[![CircleCI](https://circleci.com/gh/mtlynch/beancount-capitalone.svg?style=svg)](https://circleci.com/gh/mtlynch/beancount-capitalone)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

beancount-capitalone provides an Importer for converting CSV exports Capital One bank transactions into [Beancount](https://github.com/beancount/beancount) v2 format.

## Installation

```bash
pip install beancount-capitalone
```

## Usage

### Credit Cards

Add the Capital One Credit card importer to your account as follows:

```python
import beancount_capitalone

CONFIG = [
    beancount_capitalone.CreditImporter(
        'Liabilities:Credit-Cards:CapitalOne',
        currency='USD',
        lastfour='1234', # Replace with last four digits of your account
        account_patterns=[
          # These are example patterns. You can add your own.
          ('GITHUB', 'Expenses:Cloud-Services:Source-Hosting:Github'),
          ('Fedex',  'Expenses:Postage:FedEx'),
        ]
    ),
]
```
Once this configuration is in place, you can use `bean-extract` to convert a CapitalOne CSV export of transactions to beancount format:

```bash
bean-extract config.py 2023-03-10_transaction_download.csv
```

## API

### `account_patterns`

The `account_patterns` parameter is a list of (regex, account) pairs. For each line in your CSV, the CapitalOne importer will attempt to create a matching posting on the transaction by matching the payee, narration, or the concatenated pair to the regexes.

The regexes are in priority order, with earlier patterns taking priority over later patterns.

## Resources

See [awesome-beancount](https://awesome-beancount.com/) for other publicly available Beancount importers.
