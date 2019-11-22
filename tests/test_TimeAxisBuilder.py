from unittest import TestCase
from datetime import date, datetime, timedelta

import numpy as np

from axisutilities import Axis, WeeklyTimeAxisBuilder, RollingWindowTimeAxisBuilder, MonthlyTimeAxisBuilder, \
    TimeAxisBuilderFromDataTicks, DailyTimeAxisBuilder, FixedIntervalAxisBuilder, DailyTimeAxis
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class TestDailyTimeAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_build_00(self):
        with self.assertRaises(ValueError):
            DailyTimeAxisBuilder()\
                .build()

    def test_build_01(self):
        with self.assertRaises(ValueError):
            DailyTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 1))\
                .build()

    def test_build_02(self):
        with self.assertRaises(ValueError):
            DailyTimeAxisBuilder()\
                .set_end_date(date(2019, 1, 7))\
                .build()

    def test_build_03(self):
        with self.assertRaises(ValueError):
            DailyTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 7))\
                .set_end_date(date(2019, 1, 1))\
                .build()

    def test_build_04(self):
        start = date(2019, 1, 1)
        end = date(2019, 1, 8)

        ta = DailyTimeAxisBuilder()\
                .set_start_date(start)\
                .set_end_date(end)\
                .build()

        print("Sample TimeAxis built by DailyTimeAxis: ", ta.asJson())
        self.assertEqual(
            '{"nelem": 7, '
             '"lower_bound": [1546300800000000, 1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000, 1546819200000000], '
             '"upper_bound": [1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000, 1546819200000000, 1546905600000000], '
             '"data_ticks": [1546344000000000, 1546430400000000, 1546516800000000, 1546603200000000, 1546689600000000, 1546776000000000, 1546862400000000], '
             '"fraction": [0.5], '
             '"binding": "middle"}',
            ta.asJson()
        )
        self.assertEqual("2019-01-01 12:00:00", ta[0].asDict()["data_tick"])
        self.assertEqual("2019-01-02 12:00:00", ta[1].asDict()["data_tick"])
        self.assertEqual("2019-01-03 12:00:00", ta[2].asDict()["data_tick"])
        self.assertEqual("2019-01-04 12:00:00", ta[3].asDict()["data_tick"])
        self.assertEqual("2019-01-05 12:00:00", ta[4].asDict()["data_tick"])
        self.assertEqual("2019-01-06 12:00:00", ta[5].asDict()["data_tick"])
        self.assertEqual("2019-01-07 12:00:00", ta[6].asDict()["data_tick"])
        self.assertEqual("2019-01-01 12:00:00", ta[-7].asDict()["data_tick"])
        self.assertEqual("2019-01-02 12:00:00", ta[-6].asDict()["data_tick"])
        self.assertEqual("2019-01-03 12:00:00", ta[-5].asDict()["data_tick"])
        self.assertEqual("2019-01-04 12:00:00", ta[-4].asDict()["data_tick"])
        self.assertEqual("2019-01-05 12:00:00", ta[-3].asDict()["data_tick"])
        self.assertEqual("2019-01-06 12:00:00", ta[-2].asDict()["data_tick"])
        self.assertEqual("2019-01-07 12:00:00", ta[-1].asDict()["data_tick"])

    def test_build_05(self):
        ta = DailyTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 1)) \
                .set_n_interval(7) \
                .build()

        self.assertEqual(
            '{"nelem": 7, "lower_bound": [1546300800000000, 1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000, 1546819200000000], '
             '"upper_bound": [1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000, 1546819200000000, 1546905600000000], '
             '"data_ticks": [1546344000000000, 1546430400000000, 1546516800000000, 1546603200000000, 1546689600000000, 1546776000000000, 1546862400000000], '
             '"fraction": [0.5], '
             '"binding": "middle"}',
            ta.asJson()
        )
        self.assertEqual("2019-01-01 12:00:00", ta[0].asDict()["data_tick"])
        self.assertEqual("2019-01-02 12:00:00", ta[1].asDict()["data_tick"])
        self.assertEqual("2019-01-03 12:00:00", ta[2].asDict()["data_tick"])
        self.assertEqual("2019-01-04 12:00:00", ta[3].asDict()["data_tick"])
        self.assertEqual("2019-01-05 12:00:00", ta[4].asDict()["data_tick"])
        self.assertEqual("2019-01-06 12:00:00", ta[5].asDict()["data_tick"])
        self.assertEqual("2019-01-07 12:00:00", ta[6].asDict()["data_tick"])
        self.assertEqual("2019-01-01 12:00:00", ta[-7].asDict()["data_tick"])
        self.assertEqual("2019-01-02 12:00:00", ta[-6].asDict()["data_tick"])
        self.assertEqual("2019-01-03 12:00:00", ta[-5].asDict()["data_tick"])
        self.assertEqual("2019-01-04 12:00:00", ta[-4].asDict()["data_tick"])
        self.assertEqual("2019-01-05 12:00:00", ta[-3].asDict()["data_tick"])
        self.assertEqual("2019-01-06 12:00:00", ta[-2].asDict()["data_tick"])
        self.assertEqual("2019-01-07 12:00:00", ta[-1].asDict()["data_tick"])

    def test_build_06(self):
        axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8)
        ).build()

        self.assertListEqual(
            [1546300800000000, 1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000, 1546819200000000],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000, 1546819200000000, 1546905600000000],
            axis.upper_bound.flatten().tolist()
        )

        self.assertListEqual(
            axis.lower_bound.flatten().tolist()[1:],
            axis.upper_bound.flatten().tolist()[:-1]
        )


class TestDailyTimeAxis(TestCase):
    def test_01(self):
        start_date = date(2019, 1, 1)
        end_date = date(2019, 1, 8)

        expected_axis = DailyTimeAxisBuilder()\
            .set_start_date(start_date)\
            .set_end_date(end_date)\
            .build()

        axis = DailyTimeAxis(
            start_date=start_date,
            end_date=end_date
        )

        np.testing.assert_almost_equal(
            axis._bounds,
            expected_axis._bounds
        )

    def test_02(self):
        start_date = date(2019, 1, 1)
        end_date = date(2019, 1, 8)

        expected_axis = DailyTimeAxisBuilder(
            start_date=start_date,
            end_date=end_date
        ).build()

        axis = DailyTimeAxis(
            start_date=start_date,
            end_date=end_date
        )

        np.testing.assert_almost_equal(
            axis._bounds,
            expected_axis._bounds
        )


class TestWeeklyTimeAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_creation_01(self):
        ta = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1))\
            .set_end_date(date(2019, 1, 8))\
            .build()

        self.assertEqual(1, ta.nelem)

    def test_creation_02(self):
        # This is short of a week by one day. Hence, the interval of one week does not divide the period
        # properly
        with self.assertRaises(ValueError):
            WeeklyTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 1)) \
                .set_end_date(date(2019, 1, 7)) \
                .build()

    def test_creation_03(self):
        ta = WeeklyTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 1)) \
                .set_end_date(date(2019, 1, 15)) \
                .build()

        self.assertEqual(2, ta.nelem)

    def test_creation_04(self):
        ta = WeeklyTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 1)) \
                .set_n_interval(2) \
                .build()

        self.assertEqual(2, ta.nelem)

        self.assertEqual(
            datetime(2019, 1, 8),
            datetime.utcfromtimestamp(ta.upper_bound[0, 0] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

        self.assertEqual(
            datetime(2019, 1, 15),
            datetime.utcfromtimestamp(ta.upper_bound[0, 1] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

    def test_creation_05(self):
        ta = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        self.assertEqual(2, ta.nelem)

        self.assertEqual(
            datetime(2019, 1, 8),
            datetime.utcfromtimestamp(ta.upper_bound[0, 0] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

        self.assertEqual(
            datetime(2019, 1, 15),
            datetime.utcfromtimestamp(ta.upper_bound[0, 1] / SECONDS_TO_MICROSECONDS_FACTOR)
        )


class TestRollingWindowTimeAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_build_01(self):
        a = 1
        ta = RollingWindowTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 1))\
                .set_end_date(date(2019, 1, 15))\
                .set_window_size(7)\
                .build()

        self.assertEqual(8, ta.nelem)

        lower_bound = ta.lower_bound
        upper_bound = ta.upper_bound
        data_ticks = ta.data_ticks

        self.assertTrue(np.all(lower_bound < upper_bound))
        self.assertTrue(np.all((upper_bound - lower_bound) == 7 * 24 * 3600 * 1e6))
        self.assertTrue(np.all((lower_bound[0, 1:] - lower_bound[0, :-1]) == 24 * 3600 * 1e6))
        self.assertTrue(np.all((upper_bound[0, 1:] - upper_bound[0, :-1]) == 24 * 3600 * 1e6))
        self.assertTrue(np.all((data_ticks - lower_bound) == 3.5 * 24 * 3600 * 1e6))
        self.assertTrue(np.all((upper_bound - data_ticks) == 3.5 * 24 * 3600 * 1e6))

    def test_build_02(self):
        a = 1
        ta = RollingWindowTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7
        ).build()

        self.assertEqual(8, ta.nelem)

        lower_bound = ta.lower_bound
        upper_bound = ta.upper_bound
        data_ticks = ta.data_ticks

        self.assertTrue(np.all(lower_bound < upper_bound))
        self.assertTrue(np.all((upper_bound - lower_bound) == 7 * 24 * 3600 * 1e6))
        self.assertTrue(np.all((lower_bound[0, 1:] - lower_bound[0, :-1]) == 24 * 3600 * 1e6))
        self.assertTrue(np.all((upper_bound[0, 1:] - upper_bound[0, :-1]) == 24 * 3600 * 1e6))
        self.assertTrue(np.all((data_ticks - lower_bound) == 3.5 * 24 * 3600 * 1e6))
        self.assertTrue(np.all((upper_bound - data_ticks) == 3.5 * 24 * 3600 * 1e6))


class TestMonthlyTimeAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_build_01(self):
        ta = MonthlyTimeAxisBuilder(
            start_year=2019,
            end_year=2019
        ).build()

        self.assertEqual(12, ta.nelem)

        self.assertListEqual(
            [1546300800000000, 1548979200000000, 1551398400000000, 1554076800000000,
             1556668800000000, 1559347200000000, 1561939200000000, 1564617600000000,
             1567296000000000, 1569888000000000, 1572566400000000, 1575158400000000],
            ta.lower_bound[0, :].tolist()
        )

        self.assertListEqual(
            [1548979200000000, 1551398400000000, 1554076800000000, 1556668800000000,
             1559347200000000, 1561939200000000, 1564617600000000, 1567296000000000,
             1569888000000000, 1572566400000000, 1575158400000000, 1577836800000000],
            ta.upper_bound[0, :].tolist()
        )

        self.assertListEqual(
            ta.lower_bound[0, 1:].tolist(),
            ta.upper_bound[0, :-1].tolist()
        )

    def test_build_02(self):
        ta = MonthlyTimeAxisBuilder(
            start_year=2019,
            end_year=2020
        ).build()

        self.assertEqual(24, ta.nelem)
        self.assertListEqual(
            [1546300800000000, 1548979200000000, 1551398400000000, 1554076800000000,
             1556668800000000, 1559347200000000, 1561939200000000, 1564617600000000,
             1567296000000000, 1569888000000000, 1572566400000000, 1575158400000000,
             1577836800000000, 1580515200000000, 1583020800000000, 1585699200000000,
             1588291200000000, 1590969600000000, 1593561600000000, 1596240000000000,
             1598918400000000, 1601510400000000, 1604188800000000, 1606780800000000],
            ta.lower_bound[0, :].tolist()
        )
        self.assertListEqual(
            [1548979200000000, 1551398400000000, 1554076800000000, 1556668800000000,
             1559347200000000, 1561939200000000, 1564617600000000, 1567296000000000,
             1569888000000000, 1572566400000000, 1575158400000000, 1577836800000000,
             1580515200000000, 1583020800000000, 1585699200000000, 1588291200000000,
             1590969600000000, 1593561600000000, 1596240000000000, 1598918400000000,
             1601510400000000, 1604188800000000, 1606780800000000, 1609459200000000],
            ta.upper_bound[0, :].tolist()
        )

        self.assertListEqual(
            ta.lower_bound[0, 1:].tolist(),
            ta.upper_bound[0, :-1].tolist()
        )

    def test_build_03(self):
        ta = MonthlyTimeAxisBuilder(
            start_year=2019,
            end_year=2020,
            start_month=10,
            end_month=5
        ).build()

        self.assertEqual(8, ta.nelem)
        print(ta.lower_bound[0, :].tolist())
        self.assertListEqual(
            [1569888000000000, 1572566400000000, 1575158400000000, 1577836800000000,
             1580515200000000, 1583020800000000, 1585699200000000, 1588291200000000],
            ta.lower_bound[0, :].tolist()
        )
        print(ta.upper_bound[0, :].tolist())
        self.assertListEqual(
            [1572566400000000, 1575158400000000, 1577836800000000, 1580515200000000,
             1583020800000000, 1585699200000000, 1588291200000000, 1590969600000000],
            ta.upper_bound[0, :].tolist()
        )

        self.assertListEqual(
            ta.lower_bound[0, 1:].tolist(),
            ta.upper_bound[0, :-1].tolist()
        )


class TestTimeAxisBuilderFromDataTicks(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_build_01(self):
        data_ticks = [datetime(2019, 1, i, 12, 0, 0) for i in range(1, 8)]
        ta = TimeAxisBuilderFromDataTicks(
            data_ticks=data_ticks
        ).build()






