import csv
import datetime
import os
import re

import titlecase
from beancount.core import amount
from beancount.core import data
from beancount.core import flags
from beancount.core import number as beancount_number
from beancount.ingest import importer

_COLUMN_DATE = 'Posted Date'
_COLUMN_PAYEE = 'Description'
_COLUMN_DEBIT_AMOUNT = 'Debit'
_COLUMN_CREDIT_AMOUNT = 'Credit'

_FILENAME_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}_transaction_download.csv')


class CreditImporter(importer.ImporterProtocol):

    def __init__(self,
                 account,
                 lastfour=None,
                 currency='USD',
                 account_patterns=None):
        self._account = account
        self._last_four_account_digits = lastfour
        self._currency = currency
        self._account_patterns = []
        if account_patterns:
            for pattern, account_name in account_patterns:
                self._account_patterns.append(
                    (re.compile(pattern, flags=re.IGNORECASE), account_name))

    def _parse_amount(self, amount_raw):
        return amount.Amount(beancount_number.D(amount_raw), self._currency)

    def file_date(self, file):
        return max(map(lambda x: x.date, self.extract(file)))

    def file_account(self, _):
        return self._account

    def identify(self, file):
        match = _FILENAME_PATTERN.match(os.path.basename(file.name))
        if not match:
            return False

        with open(file.name, encoding='utf-8') as csv_file:
            for row in csv.DictReader(csv_file):
                return row['Card No.'] == self._last_four_account_digits

    def extract(self, f):
        transactions = []

        with open(f.name, encoding='utf-8') as csv_file:
            for index, row in enumerate(csv.DictReader(csv_file)):
                metadata = data.new_metadata(f.name, index)
                transaction = self._extract_transaction_from_row(row, metadata)
                if not transaction:
                    continue
                transactions.append(transaction)

        return transactions

    def _extract_transaction_from_row(self, row, metadata):
        transaction_date = datetime.datetime.strptime(row[_COLUMN_DATE],
                                                      '%Y-%m-%d').date()

        payee = row[_COLUMN_PAYEE]
        transaction_description = titlecase.titlecase(payee)

        if row[_COLUMN_DEBIT_AMOUNT]:
            transaction_amount = self._parse_amount(row[_COLUMN_DEBIT_AMOUNT])
        elif row[_COLUMN_CREDIT_AMOUNT]:
            # Negate the credit column so that it has opposite sign from debits.
            negated_credit_amount = '-' + row[_COLUMN_CREDIT_AMOUNT]
            transaction_amount = self._parse_amount(negated_credit_amount)
        else:
            return None  # 0 dollar transaction

        if transaction_amount == amount.Amount(beancount_number.D(0),
                                               self._currency):
            return None

        postings = [
            data.Posting(account=self._account,
                         units=-transaction_amount,
                         cost=None,
                         price=None,
                         flag=None,
                         meta=None)
        ]
        for pattern, account_name in self._account_patterns:
            if pattern.search(payee):
                postings.append(
                    data.Posting(account=account_name,
                                 units=transaction_amount,
                                 cost=None,
                                 price=None,
                                 flag=None,
                                 meta=None))
                break

        # For some reason, pylint thinks data.Transactions is not callable.
        # pylint: disable=not-callable
        return data.Transaction(
            meta=metadata,
            date=transaction_date,
            flag=flags.FLAG_OKAY,
            payee=None,
            narration=transaction_description,
            tags=data.EMPTY_SET,
            links=data.EMPTY_SET,
            postings=postings,
        )
