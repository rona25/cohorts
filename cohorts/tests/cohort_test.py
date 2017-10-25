from cohort_base_test import CohortTestCase

from cohorts.cohort import CohortAnalysis
from cohorts.cohort import CohortGroup


class CohortGroupTest(CohortTestCase):

    def test_invalid_group_number(self):
        tz = self.TZ_UTC
        start_ts = self.create_datetime(5, 1, 2017, 0, 0, 0, tz)
        end_ts = self.create_datetime(5, 3, 2017, 23, 59, 0, tz)

        try:
            CohortGroup('a group', 0, 3, start_ts, end_ts)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortGroup('a group', -1, 3, start_ts, end_ts)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortGroup('a group', None, 3, start_ts, end_ts)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortGroup('a group', 1, 3, start_ts, end_ts)
            # successful
        except ValueError:
            self.fail()

    def test_invalid_bucket_days(self):
        tz = self.TZ_UTC
        start_ts = self.create_datetime(5, 1, 2017, 0, 0, 0, tz)
        end_ts = self.create_datetime(5, 3, 2017, 23, 59, 0, tz)

        try:
            CohortGroup('a group', 1, 0, start_ts, end_ts)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortGroup('a group', 1, -1, start_ts, end_ts)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortGroup('a group', 1, None, start_ts, end_ts)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortGroup('a group', 1, 1, start_ts, end_ts)
            # successful
        except ValueError:
            self.fail()

    def test_is_in_group_boundaries(self):
        tz = self.TZ_UTC
        start_ts = self.create_datetime(5, 1, 2017, 0, 0, 0, tz)
        end_ts = self.create_datetime(5, 3, 2017, 23, 59, 0, tz)
        grp = CohortGroup('a group', 1, 3, start_ts, end_ts)

        self.assertTrue(
            grp.is_date_in_group(
                self.create_datetime(5, 1, 2017, 0, 0, 0, tz)
            )
        )
        self.assertTrue(
            grp.is_date_in_group(
                self.create_datetime(5, 3, 2017, 23, 59, 0, tz)
            )
        )

    def test_is_in_group_out_of_bound(self):
        tz = self.TZ_UTC
        start_ts = self.create_datetime(5, 1, 2017, 0, 0, 1, tz)
        end_ts = self.create_datetime(5, 3, 2017, 23, 59, 0, tz)
        grp = CohortGroup('a group', 1, 3, start_ts, end_ts)

        self.assertFalse(
            grp.is_date_in_group(None)
        )
        self.assertFalse(
            grp.is_date_in_group(
                self.create_datetime(5, 1, 2017, 0, 0, 0, tz)
            )
        )
        self.assertFalse(
            grp.is_date_in_group(
                self.create_datetime(5, 3, 2017, 23, 59, 1, tz)
            )
        )

        # different timezone
        self.assertFalse(
            grp.is_date_in_group(
                self.create_datetime(5, 3, 2017, 23, 59, 0, self.TZ_PST)
            )
        )
        self.assertFalse(
            grp.is_date_in_group(
                self.create_datetime(5, 3, 2017, 16, 59, 1, self.TZ_PST)
            )
        )
        self.assertTrue(
            grp.is_date_in_group(
                self.create_datetime(5, 3, 2017, 16, 59, 0, self.TZ_PST)
            )
        )

    def test_add_customer_bad_input(self):
        tz = self.TZ_UTC
        timestamp = self.create_datetime(5, 1, 2017, 0, 0, 1, tz)
        grp = CohortGroup('a group', 1, 3, timestamp, timestamp)

        try:
            grp.add_customer('', timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            grp.add_customer(0, timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            grp.add_customer(1, timestamp)
            # successful
        except ValueError:
            self.fail()

    def test_add_order_bad_input(self):
        tz = self.TZ_UTC
        timestamp = self.create_datetime(5, 1, 2017, 0, 0, 1, tz)
        grp = CohortGroup('a group', 1, 3, timestamp, timestamp)

        # bad user id
        try:
            grp.add_order('', 1, timestamp, 1)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            grp.add_order(0, 1, timestamp, 1)
            self.fail()
        except ValueError:
            # successful
            pass

        # bad order id
        try:
            grp.add_order(1, '', timestamp, 1)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            grp.add_order(1, 0, timestamp, 1)
            self.fail()
        except ValueError:
            # successful
            pass

        # bad order number
        try:
            grp.add_order(1, 1, timestamp, '')
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            grp.add_order(1, 1, timestamp, 0)
            self.fail()
        except ValueError:
            # successful
            pass

        # bad order date
        try:
            grp.add_order(1, 1, None, '')
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            grp.add_order(1, 1, timestamp, 1)
            # successful
        except ValueError:
            self.fail()

    def test_add_order(self):
        tz = self.TZ_UTC
        timestamp = self.create_datetime(5, 1, 2017, 0, 0, 1, tz)
        grp = CohortGroup('a group', 1, 3, timestamp, timestamp)

        # add an order
        grp.add_order(1, 1, timestamp, 1)
        self.assertEqual(len(grp._orders), 1)

        # add a duplicate order id
        grp.add_order(1, 1, timestamp, 2)
        self.assertEqual(len(grp._orders), 1)

        # add another order
        grp.add_order(1, 2, timestamp, 2)
        self.assertEqual(len(grp._orders), 2)

    def test_add_customer(self):
        tz = self.TZ_UTC
        timestamp = self.create_datetime(5, 1, 2017, 0, 0, 1, tz)
        grp = CohortGroup('a group', 1, 3, timestamp, timestamp)

        # add a customer
        grp.add_customer(1, timestamp)
        self.assertEqual(len(grp._customers), 1)

        # add a duplicate customer
        grp.add_customer(1, timestamp)
        self.assertEqual(len(grp._customers), 1)

        # add another customer
        grp.add_customer(2, timestamp)
        self.assertEqual(len(grp._customers), 2)

    def test_buckets(self):
        tz = self.TZ_UTC
        group_number = 2
        bucket_days = 3
        start_ts = self.create_datetime(5, 1, 2017, 0, 0, 0, tz)
        end_ts = self.create_datetime(5, 1 + (group_number * bucket_days), 2017, 23, 59, 59, tz)
        grp = CohortGroup('a group', group_number, bucket_days, start_ts, end_ts, 1)

        # setup the context
        join_date_user_1 = self.create_datetime(5, 1, 2017, 0, 0, 1, tz)
        join_date_user_2 = self.create_datetime(5, 1 + bucket_days, 2017, 0, 0, 2, tz)
        join_date_user_3 = self.create_datetime(5, 1 + bucket_days, 2017, 0, 0, 3, tz)

        # add the customers
        grp.add_customer(1, join_date_user_1)
        grp.add_customer(2, join_date_user_2)
        grp.add_customer(3, join_date_user_3)

        # add the orders
        # -- user 1
        grp.add_order(
            1,
            1,
            self.create_datetime(5, 1, 2017, 0, 0, 1, tz),
            1
        )
        grp.add_order(
            1,
            2,
            self.create_datetime(5, 1 + bucket_days, 2017, 0, 0, 1, tz),
            2
        )

        # -- user 2
        grp.add_order(
            2,
            3,
            self.create_datetime(5, 1 + bucket_days, 2017, 0, 2, 2, tz),
            1
        )
        grp.add_order(
            2,
            4,
            self.create_datetime(5, 1 + bucket_days, 2017, 2, 2, 2, tz),
            2
        )

        # -- user 3 : no orders

        # check that the buckets were created as expected
        buckets = grp.get_buckets()

        self.assertEqual(len(buckets), 2)
        self.assertEqual(len(buckets[0]['first']), 2)
        self.assertEqual(len(buckets[0]['customers']), 2)
        self.assertEqual(len(buckets[1]['first']), 0)
        self.assertEqual(len(buckets[1]['customers']), 1)


class CohortAnalysisTest(CohortTestCase):

    def test_invalid_days_per_bucket(self):
        tz = self.TZ_UTC

        try:
            CohortAnalysis(-1, timezone=tz)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortAnalysis(0, timezone=tz)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortAnalysis(None, timezone=tz)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            CohortAnalysis(1, timezone=tz)
            # successful
        except ValueError:
            self.fail()

    def test_add_customer_bad_input(self):
        tz = self.TZ_UTC
        timestamp = '2017-05-01 00:00:01'
        cohort = CohortAnalysis(1, timezone=tz)

        # bad user id
        try:
            cohort.add_customer('', timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_customer(0, timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        # bad join date
        try:
            cohort.add_customer(1, '')
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_customer(1, None)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_customer(1, self.create_datetime(5, 1, 2017, 0, 0, 1, tz))
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_customer(1, timestamp)
            # successful
        except ValueError:
            self.fail()

    def test_add_order_bad_input(self):
        tz = self.TZ_UTC
        timestamp = '2017-05-01 00:00:01'
        cohort = CohortAnalysis(1, timezone=tz)

        # bad user id
        try:
            cohort.add_order('', 1, 1, timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_order(0, 1, 1, timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        # bad order id
        try:
            cohort.add_order(1, '', 1, timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_order(1, 0, 1, timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        # bad order number
        try:
            cohort.add_order(1, 1, '', timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_order(1, 1, 0, timestamp)
            self.fail()
        except ValueError:
            # successful
            pass

        # bad order date
        try:
            cohort.add_order(1, 1, 1, None)
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_order(1, 1, 1, self.create_datetime(5, 1, 2017, 0, 0, 1, tz))
            self.fail()
        except ValueError:
            # successful
            pass

        try:
            cohort.add_order(1, 1, 1, timestamp)
            # successful
        except ValueError:
            self.fail()

    def test_add_order(self):
        tz = self.TZ_UTC
        timestamp = '2017-05-01 00:00:01'
        cohort = CohortAnalysis(1, timezone=tz)

        # add an order
        cohort.add_order(1, 1, 1, timestamp)
        cohort.add_order(1, 2, 2, timestamp)
        cohort.add_order(1, 3, 3, timestamp)
        cohort.add_order(2, 1, 1, timestamp)
        cohort.add_order(2, 2, 2, timestamp)
        cohort.add_order(3, 1, 1, timestamp)
        self.assertEqual(len(cohort._cust_orders[1]), 3)
        self.assertEqual(len(cohort._cust_orders[2]), 2)
        self.assertEqual(len(cohort._cust_orders[3]), 1)

    def test_add_customer(self):
        tz = self.TZ_UTC
        cohort = CohortAnalysis(1, timezone=tz)

        # add a customer
        cohort.add_customer(1, '2017-05-01 00:00:01')
        cohort.add_customer(2, '2017-05-01 00:02:00')
        self.assertEqual(len(cohort._customer_join_date), 2)
        self.assertEqual(
            cohort._customer_join_date[1],
            self.create_datetime(5, 1, 2017, 0, 0, 1, timezone='UTC')
        )
        self.assertEqual(
            cohort._customer_join_date[2],
            self.create_datetime(5, 1, 2017, 0, 2, 0, timezone='UTC')
        )

    def test_analyze_cohorts(self):
        tz = self.TZ_UTC
        cohort = CohortAnalysis(2, timezone=tz)

        # add a customer
        # -- group 4
        cohort.add_customer(1, '2017-05-01 00:01:00')
        cohort.add_customer(2, '2017-05-01 00:02:00')
        cohort.add_customer(3, '2017-05-02 00:03:00')
        cohort.add_customer(4, '2017-05-02 00:04:00')
        # -- group 3
        cohort.add_customer(5, '2017-05-03 00:05:00')
        cohort.add_customer(6, '2017-05-04 00:06:00')
        # -- group 2
        cohort.add_customer(7, '2017-05-05 00:07:00')
        cohort.add_customer(8, '2017-05-06 00:08:00')
        cohort.add_customer(9, '2017-05-06 00:09:00')
        # -- group 1
        cohort.add_customer(10, '2017-05-08 00:10:00')

        # add the orders
        # -- group 4
        cohort.add_order(1, 101, 1, '2017-05-08 00:08:01')  # age: 7d 7:01
        cohort.add_order(2, 201, 1, '2017-05-05 00:08:01')  # age: 4d 6:01
        cohort.add_order(3, 301, 1, '2017-05-06 00:08:01')  # age: 4d 5:01
        cohort.add_order(3, 302, 2, '2017-05-08 00:08:01')  # age: 6d 7:01
        # -- group 3
        cohort.add_order(5, 501, 1, '2017-05-04 00:08:01')  # age: 1d 3:01
        cohort.add_order(6, 601, 1, '2017-05-06 00:08:01')  # age: 2d 2:01
        # -- group 2
        cohort.add_order(7, 701, 1, '2017-05-06 00:08:01')  # age: 1d 1:01
        # -- group 1
        #   *** no orders ***

        # RUN the analysis
        cohort.analyze()

        # check that the cohort groups were created as expected
        self.assertEqual(len(cohort._cohort_groups), 4)

        # check that the customers were put in the correct groups
        self.assertEqual(cohort._cohort_groups[0].num_customers, 1)
        self.assertEqual(cohort._cohort_groups[1].num_customers, 3)
        self.assertEqual(cohort._cohort_groups[2].num_customers, 2)
        self.assertEqual(cohort._cohort_groups[3].num_customers, 4)

        # check that the orders were put in the correct groups
        self.assertEqual(cohort._cohort_groups[0].num_orders, 0)
        self.assertEqual(cohort._cohort_groups[1].num_orders, 1)
        self.assertEqual(cohort._cohort_groups[2].num_orders, 2)
        self.assertEqual(cohort._cohort_groups[3].num_orders, 4)

        # check the correct number of buckets are in each group
        self.assertEqual(len(cohort._cohort_groups[0].get_buckets()), 1)
        self.assertEqual(len(cohort._cohort_groups[1].get_buckets()), 2)
        self.assertEqual(len(cohort._cohort_groups[2].get_buckets()), 3)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()), 4)

        # check the stats in each buckets
        # -- group 1
        self.assertEqual(len(cohort._cohort_groups[0].get_buckets()[0]['customers']), 0)
        self.assertEqual(len(cohort._cohort_groups[0].get_buckets()[0]['first']), 0)
        # -- group 2
        self.assertEqual(len(cohort._cohort_groups[1].get_buckets()[0]['customers']), 1)
        self.assertEqual(len(cohort._cohort_groups[1].get_buckets()[0]['first']), 1)
        self.assertEqual(len(cohort._cohort_groups[1].get_buckets()[1]['customers']), 0)
        self.assertEqual(len(cohort._cohort_groups[1].get_buckets()[1]['first']), 0)
        # -- group 3
        self.assertEqual(len(cohort._cohort_groups[2].get_buckets()[0]['customers']), 1)
        self.assertEqual(len(cohort._cohort_groups[2].get_buckets()[0]['first']), 1)
        self.assertEqual(len(cohort._cohort_groups[2].get_buckets()[1]['customers']), 1)
        self.assertEqual(len(cohort._cohort_groups[2].get_buckets()[1]['first']), 1)
        self.assertEqual(len(cohort._cohort_groups[2].get_buckets()[2]['customers']), 0)
        self.assertEqual(len(cohort._cohort_groups[2].get_buckets()[2]['first']), 0)
        # -- group 4
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[0]['customers']), 0)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[0]['first']), 0)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[1]['customers']), 0)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[1]['first']), 0)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[2]['customers']), 2)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[2]['first']), 2)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[3]['customers']), 2)
        self.assertEqual(len(cohort._cohort_groups[3].get_buckets()[3]['first']), 1)
