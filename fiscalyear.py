"""Utilities for managing the fiscal calendar."""

from __future__ import division

import calendar
import datetime


# The first month at the start of a new fiscal year.
# By default, use the U.S. federal government's fiscal year,
# which starts on October 1st and ends on September 30th.
START_DAY = 1
START_MONTH = 10

# Number of months in each quarter
MONTHS_PER_QUARTER = 12 // 4

MIN_QUARTER = 1
MAX_QUARTER = 4


def _check_int(value):
    """Check if value is an int or int-like string.

    :param value: The value to test
    :return: The value
    :rtype: int
    :raises TypeError: If value is not an int or int-like string
    """
    if isinstance(value, int):
        return value
    elif isinstance(value, str) and value.is_digit():
        return int(value)
    else:
        raise TypeError('an int or int-like string is required (got %s)' % (
            type(value).__name__))


def _check_year(year):
    """Check if year is a valid year.

    :param year: The year to test
    :return: The year
    :rtype: int
    :raises ValueError: If the year is out of range
    """
    year = _check_int(year)

    if datetime.MINYEAR <= year <= datetime.MAXYEAR:
        return year
    else:
        raise ValueError('year must be in %d..%d' % (
            datetime.MINYEAR, datetime.MAXYEAR), year)


def _check_quarter(quarter):
    """Check if quarter is a valid quarter.

    :param quarter: The quarter to test
    :return: The quarter
    :rtype: int
    :raises ValueError: If the quarter is out of range
    """
    quarter = _check_int(quarter)

    if MIN_QUARTER <= quarter <= MAX_QUARTER:
        return quarter
    else:
        raise ValueError('quarter must be in %d..%d' % (
            MIN_QUARTER, MAX_QUARTER), quarter)


class FiscalYear(object):
    """A class representing a single fiscal year."""

    __slots__ = '_fiscal_year'

    def __new__(cls, fiscal_year):
        """Constructor.

        :param fiscal_year: The fiscal year
        :type fiscal_year: int or str
        :returns: A newly constructed FiscalYear object
        :rtype: FiscalYear
        :raises TypeError: If value is not an int or int-like string
        :raises ValueError: If the year is out of range
        """
        fiscal_year = _check_year(fiscal_year)

        self = super(FiscalYear, cls).__new__(cls)
        self._fiscal_year = fiscal_year
        return self

    def __repr__(self):
        """Convert to formal string, for repr().

        >>> fy = FiscalYear(2017)
        >>> repr(fy)
        'fiscalyear.FiscalYear(2017)'
        """
        return "%s.%s(%d)" % (self.__class__.__module__,
                              self.__class__.__name__,
                              self._fiscal_year)

    def isoformat(self):
        """Return the date range formatted according to ISO.

        This is 'YYYY-MM-DD'.

        References:
        - http://www.w3.org/TR/NOTE-datetime
        - http://www.cl.cam.ac.uk/~mgk25/iso-time.html
        """
        pass

    __str__ = isoformat

    # TODO: Implement __format__ so that you can print
    # fiscal year as 17 or 2017 (%y or %Y)

    # Read-only field accessors
    @property
    def fiscal_year(self):
        """Fiscal year."""
        return self._fiscal_year

    @property
    def start(self):
        """Start of the fiscal year.

        :rtype: datetime.datetime
        """
        return self.q1.start

    @property
    def end(self):
        """End of the fiscal year.

        :rtype: datetime.datetime
        """
        return self.q4.end

    @property
    def q1(self):
        """The first quarter of the fiscal year.

        :rtype: FiscalQuarter
        """
        return FiscalQuarter(self.fiscal_year, 1)

    @property
    def q2(self):
        """The second quarter of the fiscal year.

        :rtype: FiscalQuarter
        """
        return FiscalQuarter(self.fiscal_year, 2)

    @property
    def q3(self):
        """The third quarter of the fiscal year.

        :rtype: FiscalQuarter
        """
        return FiscalQuarter(self.fiscal_year, 3)

    @property
    def q4(self):
        """The fourth quarter of the fiscal year.

        :rtype: FiscalQuarter
        """
        return FiscalQuarter(self.fiscal_year, 4)

    # Comparisons of FiscalYear objects with other

    def __lt__(self, other):
        if isinstance(other, FiscalYear):
            return self._fiscal_year < other._fiscal_year
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, FiscalYear):
            return self._fiscal_year <= other._fiscal_year
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, FiscalYear):
            return self._fiscal_year == other._fiscal_year
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, FiscalYear):
            return self._fiscal_year != other._fiscal_year
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, FiscalYear):
            return self._fiscal_year > other._fiscal_year
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, FiscalYear):
            return self._fiscal_year >= other._fiscal_year
        return NotImplemented


class FiscalQuarter:
    def __init__(self, fiscal_year, quarter):
        assert isinstance(fiscal_year, int)
        assert isinstance(quarter, int)
        assert datetime.MINYEAR <= fiscal_year <= datetime.MAXYEAR
        assert 1 <= quarter <= 4

        self.__fiscal_year = fiscal_year
        self.__quarter = quarter

    @property
    def fiscal_year(self):
        return self.__fiscal_year

    @property
    def quarter(self):
        return self.__quarter

    @property
    def start(self):
        # Find the first month of the fiscal quarter
        month = START_MONTH
        month += (self.quarter - 1) * MONTHS_PER_QUARTER
        month %= 12
        if month == 0:
            month = 12

        # Find the calendar year of the start of the fiscal quarter
        year = self.fiscal_year
        if month >= START_MONTH:
            year -= 1

        return datetime.datetime(year, month, START_DAY, 0, 0, 0)

    @property
    def end(self):
        # Find the last month of the fiscal quarter
        month = START_MONTH
        month += self.quarter * MONTHS_PER_QUARTER - 1
        month %= 12
        if month == 0:
            month = 12

        # Find the calendar year of the end of the fiscal quarter
        year = self.fiscal_year
        if month >= START_MONTH:
            year -= 1

        # Find the last day of the last month of the fiscal quarter
        day = calendar.monthrange(year, month)[1]

        return datetime.datetime(year, month, day, 23, 59, 59)


class FiscalDate(datetime.date):
    """Wrapper around datetime.date that provides the following
    additional features:

    Attributes:
        fiscal_year: the fiscal year    [int]
        quarter:     the fiscal quarter [int: 1-4]

    Methods:
        is_q1_start: True if date is the first day of the 1st quarter
                     of the fiscal year, else False
        ...
        is_q4_start: True if date is the first day of the 4th quarter
                     of the fiscal year, else False

        is_q1_end:   True if date is the last day of the 1st quarter
                     of the fiscal year, else False
        ...
        is_q4_end:   True if date is the last day of the 4th quarter
                     of the fiscal year, else False

    The fiscal year starts on the first day of October
    and ends on the last day of September. For example, the 2018
    fiscal year starts on 10/1/2017 and ends on 9/30/2018.
    """

    @property
    def fiscal_year(self):
        """Returns the fiscal year."""

        fiscal_year = self.year
        if self.month >= START_MONTH:
            fiscal_year += 1

        return fiscal_year


    @property
    def prev_quarter_fiscal_year(self):
        """Returns the fiscal year of the previous quarter."""

        fiscal_year = self.fiscal_year
        if self.quarter == 1:
            fiscal_year -= 1

        return fiscal_year

    @property
    def next_quarter_fiscal_year(self):
        """Returns the fiscal year of the next quarter."""

        fiscal_year = self.fiscal_year
        if self.quarter == 4:
            fiscal_year += 1

        return fiscal_year

    @property
    def quarter(self):
        """Returns the quarter of the fiscal year."""

        month = self.month
        month -= START_MONTH
        if month < 0:
            month += 12
        quarter = month // MONTHS_PER_QUARTER + 1

        return quarter

    @property
    def prev_quarter(self):
        """Returns the previous quarter."""

        quarter = self.quarter - 1
        if quarter == 0:
            quarter = 4

        return quarter

    @property
    def next_quarter(self):
        """Returns the next quarter."""

        quarter = self.quarter + 1
        if quarter == 5:
            quarter = 1

        return quarter

    def is_quarter_start(self, quarter):
        start = FiscalQuarter(self.fiscal_year, quarter).start.date()

        return self == start

    def is_q1_start(self):
        return self.is_quarter_start(1)

    def is_q2_start(self):
        return self.is_quarter_start(2)

    def is_q3_start(self):
        return self.is_quarter_start(3)

    def is_q4_start(self):
        return self.is_quarter_start(4)

    def is_quarter_end(self, quarter):
        end = FiscalQuarter(self.fiscal_year, quarter).end.date()

        return self == end

    def is_q1_end(self):
        return self.is_quarter_end(1)

    def is_q2_end(self):
        return self.is_quarter_end(2)

    def is_q3_end(self):
        return self.is_quarter_end(3)

    def is_q4_end(self):
        return self.is_quarter_end(4)
