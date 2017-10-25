import argparse
import csv
import pendulum
import sys
import time

from collections import defaultdict
from prettytable import PrettyTable


class CohortAnalysis(object):
    def __init__(
            self,
            days_per_bucket=7,
            timezone='UTC',
            verbosity=0):
        """Constructor.

        :param days_per_bucket: the number of days per cohort group.
        :param timezone: the timezone used to perform the cohort analysis.
        :param verbosity: integer > 0 that represents the debugging verbosity.
        """
        super(CohortAnalysis, self).__init__()

        if not days_per_bucket or days_per_bucket <= 0:
            raise ValueError('days per bucket must be greater than 0')

        self._customer_join_date = defaultdict(dict)
        self._cust_orders = defaultdict(list)
        self._min_customer_join_date = None
        self._max_customer_join_date = None
        self._days_per_bucket = days_per_bucket
        self._cohort_groups = list()
        self._verbosity = verbosity

        if timezone:
            self._timezone = timezone
        else:
            self._timezone = 'UTC'

    def add_customer(self, user_id, date_created):
        """Add a customer to be analyzed.

        :param user_id: the user id associated with the order.
        :param date_created: the join date of the customer, specified as a date/time
            string in UTC (e.g., "2015-07-03 22:57:23")

        :return: boolean whether the customer was added successfully
        """

        if not (user_id and date_created):
            raise ValueError('all arguments are required')

        if not isinstance(date_created, basestring):
            raise ValueError('order date must be a UTC string format "YYYY-MM-DD HH:mm:ss"')

        join_date = pendulum.parse(date_created, tz='UTC').in_timezone(self._timezone)

        if not self._min_customer_join_date:
            self._min_customer_join_date = join_date
        elif join_date < self._min_customer_join_date:
            self._min_customer_join_date = join_date

        if not self._max_customer_join_date:
            self._max_customer_join_date = join_date
        elif join_date > self._max_customer_join_date:
            self._max_customer_join_date = join_date

        self._customer_join_date[int(user_id)] = join_date

        return True

    def add_order(
            self,
            user_id,
            order_id,
            order_number,
            date_created):
        """Add an order to be analyzed.

        :param user_id: the user id associated with the order.
        :param order_id: the order id.
        :param order_number: the order number with respect to that particular customer.
        :param date_created: the order date, specified as a date/time string in UTC
            (e.g., "2015-07-03 22:57:23")

        :return: boolean whether the order was added successfully
        """

        if not (user_id and order_id and order_number and date_created):
            raise ValueError('all arguments are required')

        if not isinstance(date_created, basestring):
            raise ValueError('order date must be a UTC string format "YYYY-MM-DD HH:mm:ss"')

        order_date = pendulum.parse(date_created, tz='UTC').in_timezone(self._timezone)

        self._cust_orders[int(user_id)].append({
            'id': int(order_id),
            'order_number': int(order_number),
            'created': order_date
        })

        return True

    def analyze(self):
        """Perform the actual cohort analysis and generate the summarized data
        based on the customer and order collected.
        """
        if self._verbosity > 0:
            print 'DEBUG: analyzing - min cust join date:', self._min_customer_join_date
            print 'DEBUG: analyzing - max cust join date:', self._max_customer_join_date

        # create the cohort groups
        cohort_groups = self._generate_groups(
            self._min_customer_join_date,
            self._max_customer_join_date,
            self._timezone,
            self._days_per_bucket,
        )
        if not cohort_groups:
            raise ValueError('no groups were created')

        # reverse sort the customers since the cohort groups are also returned by reverse date
        rev_sorted_customer_ids = sorted(
            self._customer_join_date.keys(),
            key=lambda x: self._customer_join_date[x],
            reverse=True
        )

        # add all the customers to the appropriate cohort groups
        num_cohort_groups = len(cohort_groups)
        grp_num = 0
        cust_count = 0
        cohort_grp = cohort_groups[grp_num]
        for user_id in rev_sorted_customer_ids:
            cust_count += 1
            cust_join_date = self._customer_join_date[user_id]

            # find the right cohort group
            is_in_group = cohort_grp.is_date_in_group(cust_join_date)
            while not is_in_group and (grp_num < num_cohort_groups):
                grp_num += 1
                cohort_grp = cohort_groups[grp_num]
                is_in_group = cohort_grp.is_date_in_group(cust_join_date)

            cohort_grp.add_customer(user_id, cust_join_date)

        if self._verbosity > 0:
            print 'DEBUG: # customers:', cust_count
            print 'DEBUG: # exp #:', len(self._customer_join_date)

        # iterate thru each customer to get all of their orders
        users_found = 0
        for user_id in self._cust_orders.keys():
            # skip any customers that we do not have any join date information
            if not self._customer_join_date.get(user_id):
                continue

            user_join_date = self._customer_join_date[user_id]
            customer_orders_list = sorted(
                self._cust_orders[user_id],
            )

            # find the appropriate cohort bucket
            found_group = None
            for grp in cohort_groups:
                if grp.is_date_in_group(user_join_date):
                    found_group = grp
                    break

            if not found_group:
                # should never get this condition with no cohort group found
                raise ValueError('cohort group not found')

            # make sure the orders are unique
            order_num = 0
            for order in customer_orders_list:
                order_id = order['id']
                order_date = order['created']

                order_num += 1
                found_group.add_order(
                    user_id,
                    order_id,
                    order_date,
                    order_num
                )

            users_found += 1

        # data grouping complete
        self._cohort_groups = cohort_groups

    def print_table(self, max_groups=0):
        """Displays the cohort groups.

        :param max_groups: the number of cohort groups to display; <= 0 shows all groups.
        """
        cohort_grps = self._cohort_groups
        num_cohort_groups = len(cohort_grps)

        if max_groups <= 0 or max_groups > num_cohort_groups:
            num_groups_to_output = num_cohort_groups
        else:
            num_groups_to_output = max_groups

        # inital column headings
        fields = ['Cohort', 'Customers']

        # generate the dynamic table column names
        count = 0
        for i in range(num_cohort_groups):
            if max_groups and count >= max_groups:
                break

            label = '{}-{} days'.format(
                (i * self._days_per_bucket),
                ((i + 1) * self._days_per_bucket) - 1
            )
            fields.append(label)
            count += 1

        ptable = PrettyTable(fields)
        ptable.align = 'l'

        # add the row/cell data to the table
        count = 0
        for grp in cohort_grps:
            if count >= num_groups_to_output:
                break

            row_data = [
                grp.label,
                '{} customers'.format(grp.num_customers),
                ]

            # for each cohort group, get the order age buckets
            bucket_count = 0
            for age_bucket in grp.get_buckets():
                num_customers_with_orders = len(age_bucket['customers'] or [])
                num_first_orders = len(age_bucket['first'] or [])

                if grp.num_customers <= 0:
                    cust_order_pct = 0
                    first_order_pct = 0
                else:
                    cust_order_pct = float(num_customers_with_orders * 100) / grp.num_customers
                    first_order_pct = float(num_first_orders * 100) / grp.num_customers

                # generate the intended cell format
                cell_text = '{}% orderers ({})\n{}% 1st time ({})'.format(
                    int(round(cust_order_pct, 0)),
                    num_customers_with_orders,
                    int(round(first_order_pct, 0)),
                    num_first_orders
                )

                row_data.append(cell_text)
                bucket_count += 1

            # fill the empty cells with blanks
            for i in range(num_groups_to_output - bucket_count):
                row_data.append('')

            # add the row data to the table
            ptable.add_row(row_data)

            count += 1

        print ptable

    def _generate_groups(
            self,
            input_start_date,
            input_end_date,
            timezone,
            days_per_bucket):

        local_start_date = input_start_date.in_timezone(timezone)
        local_end_date = input_end_date.in_timezone(timezone).at(23, 59, 59)

        count = 1
        groups = list()
        while local_start_date < local_end_date:
            next_end_date = local_end_date.subtract(days=days_per_bucket)

            bucket = CohortGroup(
                count,
                count,
                days_per_bucket,
                next_end_date.add(seconds=1),
                local_end_date,
                verbosity=self._verbosity
            )
            groups.append(bucket)

            local_end_date = next_end_date
            count += 1

        return groups


class CohortGroup(object):
    def __init__(
            self,
            name,
            group_number,
            bucket_days,
            start_date,
            end_date,
            verbosity=0):
        """Constructor.

        :param name: a descriptive name for this group.
        :param group_number: the number of this group (integer > 0).
        :param bucket_days: the number of days in this group.
        :param start_date: the start date/time of this group.
        :param end_date: the end date/time of this group.
        :param verbosity: verbosity integer > 0 that represents the debugging verbosity.
        """
        super(CohortGroup, self).__init__()

        if not (start_date and end_date):
            raise ValueError('group start date and end date required')
        elif start_date > end_date:
            raise ValueError('group start date must be before end date')

        if not group_number or group_number <= 0:
            raise ValueError('group number must be greater than 0')

        if not bucket_days or bucket_days <= 0:
            raise ValueError('group bucket days must be greater than 0')

        self._name = name
        self._group_number = group_number
        self._bucket_days = bucket_days
        self._start_date = start_date
        self._end_date = end_date
        self._verbosity = verbosity
        self._customers = dict()
        self._orders = dict()

    @property
    def end_date(self):
        return self._end_date

    @property
    def label(self):
        result = '{start}-{end}'.format(
            start=self._start_date.format('M/D', formatter='alternative'),
            end=self._end_date.format('M/D', formatter='alternative'),
        )

        return result

    @property
    def name(self):
        return self._name

    @property
    def num_customers(self):
        return len(self._customers)

    @property
    def num_orders(self):
        return len(self._orders)

    @property
    def start_date(self):
        return self._start_date

    def is_date_in_group(self, date_value):
        """Determines whether the specified date is within the range of this group.

        :param date_value: the date to check whether it is in the current cohort group.

        :return: boolean whether the date is in this cohort group
        """
        if not date_value:
            return False

        if self._verbosity > 2:
            print 'START: {} / END: {} / VALUE: {}'.format(
                self._start_date, self._end_date, date_value)

        result = date_value.between(
            self._start_date,
            self._end_date,
            equal=True
        )

        return result

    def add_customer(
            self,
            user_id,
            join_date):
        """Add a customer to this group.

        :param user_id: the user id associated with the order.
        :param join_date: the join date of the customer for the order.

        :return: boolean whether the order was added successfully
        """

        # error checking
        if not (user_id and join_date):
            raise ValueError('all customer params are required')

        self._customers[user_id] = {
            'join_date': join_date,
        }

        return True

    def add_order(
            self,
            user_id,
            order_id,
            order_date,
            order_num):
        """Add an order to this group.

        :param user_id: the user id associated with the order.
        :param order_id: the order id.
        :param order_date: the order date.
        :param order_num: the order number with respect to that particular customer.

        :return: boolean whether the order was added successfully
        """

        # error checking
        if not (user_id and order_id and order_date and order_num):
            raise ValueError('all order params are required')

        # ignore duplicate orders
        if order_id in self._orders:
            return False

        self._orders[order_id] = {
            'user_id': user_id,
            'order_id': order_id,
            'order_num': order_num,
            'order_date': order_date,
        }

        return True

    def get_buckets(self):
        """Gets the buckets that represents cohorts of customers of when
        they made their purchases relative on their signup date.

        :return: list of cohort buckets (dict)
            {
                "customers": set(<user id>), - customers that made an order
                "first": set(<user id>), - customers that made their first order

            }
        """
        customer_age_buckets = list()

        # create the buckets
        for i in range(self._group_number):
            customer_age_buckets.append({
                'num': i + 1,
                'customers': set(),
                'first': set(),
            })

        # add the customer orders in the appropriate buckets
        for order_id in sorted(self._orders.keys(), key=lambda x: self._orders[x]['user_id']):
            order = self._orders[order_id]
            user_id = order['user_id']
            order_num = order['order_num']
            order_date = order['order_date']

            # try to resolve the user join date
            user_join_date = self._customers.get(user_id) and self._customers[user_id].get('join_date')
            if not user_join_date:
                # skip since we don't have the join date
                continue

            # calculate the time between the order and the user's join date
            delta = order_date.diff(user_join_date, True)
            bucket_index = (delta.in_days() / self._bucket_days)

            # ignore orders in future buckets
            if bucket_index >= self._group_number:
                continue

            customer_age_buckets[bucket_index]['customers'].add(user_id)
            if order_num == 1:
                customer_age_buckets[bucket_index]['first'].add(user_id)

        return customer_age_buckets


def get_objects_from_file(file_path):
    """Loads the CSV files into dictionary objects.

    :param file_path: the path to the CSV data file.

    :return: list of dictionaries representing each row in the CSV file
    """

    # validate the specified file
    result = []

    customer_fields = None
    num_fields = 0
    with open(file_path, 'rb') as csvfile:
        file_reader = csv.reader(
            csvfile,
            delimiter=',',
            quotechar='"',
        )

        line_num = 0
        for line_parts in file_reader:
            line_num += 1
            if line_num == 1:
                customer_fields = line_parts
                num_fields = len(line_parts)
                continue

            obj = dict([(customer_fields[i], line_parts[i]) for i in range(num_fields)])
            result.append(obj)

    return result


def main():
    start = time.time()

    # parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--limit', type=int, default=0, help='num cohorts to display')
    parser.add_argument('-tz', '--timezone', default='UTC', help='the timezone associated with the cohort groups')
    parser.add_argument('-d', '--days-per-bucket', metavar='DAYS', type=int, default=7, help='number of days per bucket')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help='display debugging information')
    parser.add_argument('orders_file', help='the orders CSV file')
    parser.add_argument('customers_file', help='the customers CSV file')
    args = parser.parse_args()

    orders_file = args.orders_file
    customers_file = args.customers_file
    num_cohorts_to_display = args.limit
    timezone = args.timezone
    days_per_bucket = args.days_per_bucket
    verbosity = args.verbosity

    if verbosity > 0:
        print 'ARG: orders_file     = [{}]'.format(orders_file)
        print 'ARG: customers_file  = [{}]'.format(customers_file)
        print 'ARG: display size    = [{}]'.format(num_cohorts_to_display)
        print 'ARG: timezone        = [{}]'.format(timezone)
        print 'ARG: verbosity       = [{}]'.format(verbosity)

    # load the csv data files
    checkpoint = time.time()
    customers = get_objects_from_file(customers_file)
    orders = get_objects_from_file(orders_file)

    if verbosity > 0:
        print 'DEBUG: num customers:', len(customers)
        print 'DEBUG: num orders:', len(orders)
        print 'DEBUG: ~~~ 1) time:', time.time() - checkpoint, '(load files)'

    # start the cohorts initialization
    checkpoint = time.time()
    cohorts = CohortAnalysis(
        timezone=timezone,
        days_per_bucket=days_per_bucket,
        verbosity=verbosity
    )

    # -- load all the customers into the cohorts
    for i in customers:
        cohorts.add_customer(
            i['id'],
            i['created']
        )

    if verbosity > 0:
        print 'DEBUG: ~~~ 2) time:', time.time() - checkpoint, '(add customers)'

    checkpoint = time.time()

    # -- load all the customer orders into the cohorts
    for i in orders:
        cohorts.add_order(
            i['user_id'],
            i['id'],
            i['order_number'],
            i['created'],
        )

    if verbosity > 0:
        print 'DEBUG: ~~~ 3) time:', time.time() - checkpoint, '(add orders)'

    # -- perform the actual cohort analysis
    checkpoint = time.time()
    cohorts.analyze()

    if verbosity > 0:
        print 'DEBUG: ~~~ 4) time:', time.time() - checkpoint, '(analyze)'

    # -- generate the summarized output
    checkpoint = time.time()
    cohorts.print_table(num_cohorts_to_display)

    if verbosity > 0:
        print 'DEBUG: ~~~ 5) time:', time.time() - checkpoint, '(print table)'
        print 'DEBUG: $$$$ TOTAL TIME:', time.time() - start

    return 0


if __name__ == "__main__":
    sys.exit(main())
