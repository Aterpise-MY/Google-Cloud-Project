"""Failure types raised by the data layer and handled by report.py."""


class BillingTableMissing(Exception):
    """The billing export table does not exist (export not delivering yet)."""


class BillingQueryError(Exception):
    """A BigQuery call failed for another reason."""
