from unittest import TestCase
from datetime import date, datetime, timedelta

import numpy as np

from axisutilities import Axis, WeeklyTimeAxisBuilder, RollingWindowTimeAxisBuilder, MonthlyTimeAxisBuilder, \
    TimeAxisBuilderFromDataTicks, DailyTimeAxisBuilder, FixedIntervalAxisBuilder, DailyTimeAxis
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR
from axisutilities.timeaxisbuilders import TimeAxisBuilder, WeeklyTimeAxis, RollingWindowTimeAxis, MonthlyTimeAxis, \
    TimeAxisFromDataTicks


class TestTimeAxisBuilder(TestCase):
    def test_to_utc_timestamp_01(self):
        ts = TimeAxisBuilder.to_utc_timestamp(date(2019, 1, 1))
        self.assertEqual(
            1546300800*1000000,
            ts
        )

    def test_to_utc_timestamp_02(self):
        ts = TimeAxisBuilder.to_utc_timestamp(None)
        self.assertEqual(
            None,
            ts
        )

    def test_to_utc_timestamp_01(self):
        ts = TimeAxisBuilder.to_utc_timestamp(date(1970, 1, 1))
        self.assertEqual(
            0,
            ts
        )


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

    def test_auxilary_builder_method(self):
        axis = DailyTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8)
        )

        self.assertListEqual(
            [1546300800000000, 1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000,
             1546819200000000],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [1546387200000000, 1546473600000000, 1546560000000000, 1546646400000000, 1546732800000000, 1546819200000000,
             1546905600000000],
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

    def test_different_unit_01(self):
        axis_ms = DailyTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8)
        )

        axis_s = DailyTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8),
            second_conversion_factor=1
        )

        for e in zip(axis_ms.lower_bound.flatten().tolist(), axis_s.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * SECONDS_TO_MICROSECONDS_FACTOR)

        for e in zip(axis_ms.upper_bound.flatten().tolist(), axis_s.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * SECONDS_TO_MICROSECONDS_FACTOR)

        for e in zip(axis_ms.data_ticks.flatten().tolist(), axis_s.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * SECONDS_TO_MICROSECONDS_FACTOR)

    def test_different_unit_02(self):
        axis_ms = DailyTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8)
        )

        second_to_day = 1 / 24 / 60 / 60

        axis_d = DailyTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8),
            second_conversion_factor=second_to_day
        )

        for e in zip(axis_ms.lower_bound.flatten().tolist(), axis_d.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], int(e[1] / second_to_day * SECONDS_TO_MICROSECONDS_FACTOR))

        for e in zip(axis_ms.upper_bound.flatten().tolist(), axis_d.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], int(e[1] / second_to_day * SECONDS_TO_MICROSECONDS_FACTOR))

    def test_different_unit_03(self):
        axis_ms = DailyTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8)
        )

        second_to_hour = 1 / 24 / 60

        axis_h = DailyTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 8),
            second_conversion_factor=second_to_hour
        )

        for e in zip(axis_ms.lower_bound.flatten().tolist(), axis_h.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], int(e[1] / second_to_hour * SECONDS_TO_MICROSECONDS_FACTOR))

        for e in zip(axis_ms.upper_bound.flatten().tolist(), axis_h.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], int(e[1] / second_to_hour * SECONDS_TO_MICROSECONDS_FACTOR))


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


class TestWeeklyTimeAxis(TestCase):
    def test_01(self):
        ta = WeeklyTimeAxis(
            start_date=date(2019, 1, 1),
            n_interval=2
        )

        self.assertEqual(2, ta.nelem)

        self.assertEqual(
            datetime(2019, 1, 8),
            datetime.utcfromtimestamp(ta.upper_bound[0, 0] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

        self.assertEqual(
            datetime(2019, 1, 15),
            datetime.utcfromtimestamp(ta.upper_bound[0, 1] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

    def test_different_unit_01(self):
        ta_ms = WeeklyTimeAxis(
            start_date=date(2019, 1, 1),
            n_interval=2
        )

        ta_s = WeeklyTimeAxis(
            start_date=date(2019, 1, 1),
            n_interval=2,
            second_conversion_factor=1
        )

        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_s.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_s.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_s.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

    def test_different_unit_02(self):
        ta_ms = WeeklyTimeAxis(
            start_date=date(2019, 1, 1),
            n_interval=2
        )

        ta_h = WeeklyTimeAxis(
            start_date=date(2019, 1, 1),
            n_interval=2,
            second_conversion_factor=1 / 3600
        )

        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_h.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 3600e6)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_h.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 3600e6)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_h.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 3600e6)


class TestRollingWindowTimeAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_build_01(self):
        tmp_ta = RollingWindowTimeAxisBuilder()
        tmp_ta.set_start_date(date(2019, 1, 1))

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


class TestRollingWindowTimeAxis(TestCase):
    def test_01(self):
        ta = RollingWindowTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7
        )

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

    def test_different_unit_01(self):
        ta_ms = RollingWindowTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7
        )

        ta_s = RollingWindowTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7,
            second_conversion_factor=1
        )


        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_s.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_s.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_s.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

    def test_different_unit_02(self):
        ta_ms = RollingWindowTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7
        )

        ta_h = RollingWindowTimeAxis(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7,
            second_conversion_factor=(1 / 3600)
        )

        self.assertEqual(ta_ms.nelem, ta_h.nelem)

        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_h.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_h.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_h.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)


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

        self.assertListEqual(
            [1569888000000000, 1572566400000000, 1575158400000000, 1577836800000000,
             1580515200000000, 1583020800000000, 1585699200000000, 1588291200000000],
            ta.lower_bound[0, :].tolist()
        )

        self.assertListEqual(
            [1572566400000000, 1575158400000000, 1577836800000000, 1580515200000000,
             1583020800000000, 1585699200000000, 1588291200000000, 1590969600000000],
            ta.upper_bound[0, :].tolist()
        )

        self.assertListEqual(
            ta.lower_bound[0, 1:].tolist(),
            ta.upper_bound[0, :-1].tolist()
        )


class TestMonthlyTimeAxis(TestCase):
    def test_build_03(self):
        ta = MonthlyTimeAxis(
            start_year=2019,
            end_year=2020,
            start_month=10,
            end_month=5
        )

        self.assertEqual(8, ta.nelem)

        self.assertListEqual(
            [1569888000000000, 1572566400000000, 1575158400000000, 1577836800000000,
             1580515200000000, 1583020800000000, 1585699200000000, 1588291200000000],
            ta.lower_bound[0, :].tolist()
        )

        self.assertListEqual(
            [1572566400000000, 1575158400000000, 1577836800000000, 1580515200000000,
             1583020800000000, 1585699200000000, 1588291200000000, 1590969600000000],
            ta.upper_bound[0, :].tolist()
        )

        self.assertListEqual(
            ta.lower_bound[0, 1:].tolist(),
            ta.upper_bound[0, :-1].tolist()
        )

    def test_different_unit_01(self):
        ta_ms = MonthlyTimeAxis(
            start_year=2019,
            end_year=2020,
            start_month=10,
            end_month=5
        )

        ta_s = MonthlyTimeAxis(
            start_year=2019,
            end_year=2020,
            start_month=10,
            end_month=5,
            second_conversion_factor=1
        )

        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_s.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_s.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_s.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

    def test_different_unit_02(self):
        ta_ms = MonthlyTimeAxis(
            start_year=2019,
            end_year=2020,
            start_month=10,
            end_month=5
        )

        ta_h = MonthlyTimeAxis(
            start_year=2019,
            end_year=2020,
            start_month=10,
            end_month=5,
            second_conversion_factor=(1 / 3600)
        )

        self.assertEqual(ta_ms.nelem, ta_h.nelem)

        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_h.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_h.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_h.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)


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

        interval = ((ta.upper_bound - ta.lower_bound) / 1000000).flatten().tolist()
        np.testing.assert_almost_equal(interval, 86400.0)

        np.testing.assert_almost_equal(
            (ta.upper_bound - ta.data_ticks).flatten(),
            (ta.data_ticks - ta.lower_bound).flatten()
        )


class TestTimeAxisFromDataTicks(TestCase):
    def test_01(self):
        data_ticks = [datetime(2019, 1, i, 12, 0, 0) for i in range(1, 8)]
        ta = TimeAxisFromDataTicks(
            data_ticks=data_ticks
        )

        interval = ((ta.upper_bound - ta.lower_bound) / 1000000).flatten().tolist()
        np.testing.assert_almost_equal(interval, 86400.0)

        np.testing.assert_almost_equal(
            (ta.upper_bound - ta.data_ticks).flatten(),
            (ta.data_ticks - ta.lower_bound).flatten()
        )

    def test_different_unit_01(self):
        data_ticks = [datetime(2019, 1, i, 12, 0, 0) for i in range(1, 8)]
        ta_ms = TimeAxisFromDataTicks(
            data_ticks=data_ticks
        )

        ta_s = TimeAxisFromDataTicks(
            data_ticks=data_ticks,
            second_conversion_factor=1
        )

        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_s.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_s.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_s.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 1000000)

    def test_different_unit_02(self):
        data_ticks = [datetime(2019, 1, i, 12, 0, 0) for i in range(1, 8)]
        ta_ms = TimeAxisFromDataTicks(
            data_ticks=data_ticks
        )

        ta_h = TimeAxisFromDataTicks(
            data_ticks=data_ticks,
            second_conversion_factor=(1 / 3600)
        )

        self.assertEqual(ta_ms.nelem, ta_h.nelem)

        for e in zip(ta_ms.lower_bound.flatten().tolist(), ta_h.lower_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)

        for e in zip(ta_ms.upper_bound.flatten().tolist(), ta_h.upper_bound.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)

        for e in zip(ta_ms.data_ticks.flatten().tolist(), ta_h.data_ticks.flatten().tolist()):
            self.assertEqual(e[0], e[1] * 36e8)





