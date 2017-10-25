import pendulum
import unittest


class CohortTestCase(unittest.TestCase):
    TZ_UTC = 'UTC'
    TZ_PST = 'America/Los_Angeles'
    TZ_EST = 'America/New_York'

    def setUp(self):
        super(CohortTestCase, self).setUp()

        # set static now time
        known = pendulum.create(2001, 5, 12, 15, 42, 25)
        pendulum.set_test_now(known)

    def tearDown(self):
        super(CohortTestCase, self).tearDown()

    def create_datetime(
            self,
            month, day, year,
            hour, minute, seconds,
            timezone='UTC'):

        if timezone:
            ts = pendulum.create(
                year, month, day,
                hour, minute, seconds,
                tz=timezone
            )
        else:
            ts = pendulum.create(
                year, month, day,
                hour, minute, seconds,
                tz=self.TZ_UTC
            )

        return ts
