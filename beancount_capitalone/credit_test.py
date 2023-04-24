import io
import textwrap

import pytest  # NOQA, pylint: disable=unused-import
from beancount.ingest import extract

from . import CreditImporter


def _unindent(indented):
    return textwrap.dedent(indented).lstrip()


def _stringify_directives(directives):
    f = io.StringIO()
    extract.print_extracted_entries(directives, f)
    return f.getvalue()


def test_identifies_capitalone_credit_file(tmp_path):
    capitalone_file = tmp_path / '2023-03-10_transaction_download.csv'
    capitalone_file.write_text(
        _unindent("""
            Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
            2023-02-21,2023-02-22,1234,SHOPIFY* 169483256,Merchandise,528.55,
            """))

    with capitalone_file.open() as f:
        assert CreditImporter(account='Liabilities:Credit-Cards:CapitalOne',
                              lastfour='1234').identify(f)


def test_extracts_spend(tmp_path):
    capitalone_file = tmp_path / '2023-03-10_transaction_download.csv'
    capitalone_file.write_text(
        _unindent("""
            Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
            2023-02-21,2023-02-22,1234,SHOPIFY* 169483256,Merchandise,528.55,
            """))

    with capitalone_file.open() as f:
        directives = CreditImporter(
            account='Liabilities:Credit-Cards:CapitalOne',
            lastfour='1234').extract(f)

    assert _unindent("""
        2023-02-22 * "Shopify* 169483256"
          Liabilities:Credit-Cards:CapitalOne  -528.55 USD
        """.rstrip()) == _stringify_directives(directives).strip()


def test_extracts_spend_with_matching_transaction(tmp_path):
    capitalone_file = tmp_path / '2023-03-10_transaction_download.csv'
    capitalone_file.write_text(
        _unindent("""
            Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
            2023-02-21,2023-02-22,1234,SHOPIFY* 169483256,Merchandise,528.55,
            """))

    with capitalone_file.open() as f:
        directives = CreditImporter(
            account='Liabilities:Credit-Cards:CapitalOne',
            lastfour='1234',
            account_patterns=[
                ('Shopify', 'Expenses:Cloud-Services:Shopify'),
            ]).extract(f)

    assert _unindent("""
        2023-02-22 * "Shopify* 169483256"
          Liabilities:Credit-Cards:CapitalOne  -528.55 USD
          Expenses:Cloud-Services:Shopify       528.55 USD
        """.rstrip()) == _stringify_directives(directives).strip()


def test_extracts_cashback(tmp_path):
    capitalone_file = tmp_path / '2023-03-10_transaction_download.csv'
    capitalone_file.write_text(
        _unindent("""
            Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
            2023-03-03,2023-03-03,1234,CREDIT-CASH BACK REWARD,Payment/Credit,,32.42
            """))

    with capitalone_file.open() as f:
        directives = CreditImporter(
            account='Income:Credit-Card-Rewards:CapitalOne-Rewards',
            lastfour='1234').extract(f)

    assert _unindent("""
        2023-03-03 * "Credit-Cash Back Reward"
          Income:Credit-Card-Rewards:CapitalOne-Rewards  32.42 USD
        """.rstrip()) == _stringify_directives(directives).strip()
