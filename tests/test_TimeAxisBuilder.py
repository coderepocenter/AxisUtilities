from unittest import TestCase
from datetime import date, datetime, timedelta

import numpy as np

from axisutilities import Axis, WeeklyTimeAxisBuilder, RollingWindowTimeAxisBuilder, MonthlyTimeAxisBuilder, \
    TimeAxisBuilderFromDataTicks, DailyTimeAxisBuilder, FixedIntervalTimeAxisBuilder
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class TestFixedIntervalTimeAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_creation_01(self):
        start = int(datetime(2019, 1, 1).timestamp() * SECONDS_TO_MICROSECONDS_FACTOR)
        end = int(datetime(2019, 1, 8).timestamp() * SECONDS_TO_MICROSECONDS_FACTOR)
        interval = int(timedelta(days=1).total_seconds() * SECONDS_TO_MICROSECONDS_FACTOR)
        ta = FixedIntervalTimeAxisBuilder()\
            .set_start(start)\
            .set_end(end)\
            .set_interval(interval)\
            .build()

        print("Sample TimeAxis built by FixedIntervalTimeAxisBuilder: ", ta.asJson())
        self.assertEqual(
            '{"nelem": 7, '
            '"lower_bound": [1546326000000000, 1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000], '
             '"upper_bound": [1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000, 1546930800000000], '
             '"data_ticks": [1546369200000000, 1546455600000000, 1546542000000000, 1546628400000000, 1546714800000000, 1546801200000000, 1546887600000000], '
             '"fraction": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], '
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
             '"lower_bound": [1546326000000000, 1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000], '
             '"upper_bound": [1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000, 1546930800000000], '
             '"data_ticks": [1546369200000000, 1546455600000000, 1546542000000000, 1546628400000000, 1546714800000000, 1546801200000000, 1546887600000000], '
             '"fraction": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], '
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
            '{"nelem": 7, '
            '"lower_bound": [1546326000000000, 1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000], '
            '"upper_bound": [1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000, 1546930800000000], '
            '"data_ticks": [1546369200000000, 1546455600000000, 1546542000000000, 1546628400000000, 1546714800000000, 1546801200000000, 1546887600000000], '
            '"fraction": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], '
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
            datetime.fromtimestamp(ta.upper_bound[0, 0] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

        self.assertEqual(
            datetime(2019, 1, 15),
            datetime.fromtimestamp(ta.upper_bound[0, 1] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

    def test_creation_05(self):
        ta = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        self.assertEqual(2, ta.nelem)

        self.assertEqual(
            datetime(2019, 1, 8),
            datetime.fromtimestamp(ta.upper_bound[0, 0] / SECONDS_TO_MICROSECONDS_FACTOR)
        )

        self.assertEqual(
            datetime(2019, 1, 15),
            datetime.fromtimestamp(ta.upper_bound[0, 1] / SECONDS_TO_MICROSECONDS_FACTOR)
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
            [1546326000000000, 1549004400000000, 1551423600000000, 1554102000000000,
             1556694000000000, 1559372400000000, 1561964400000000, 1564642800000000,
             1567321200000000, 1569913200000000, 1572591600000000, 1575183600000000],
            ta.lower_bound[0, :].tolist()
        )
        self.assertListEqual(
            [1548918000000000, 1551337200000000, 1554015600000000, 1556607600000000,
             1559286000000000, 1561878000000000, 1564556400000000, 1567234800000000,
             1569826800000000, 1572505200000000, 1575097200000000, 1577775600000000],
            ta.upper_bound[0, :].tolist()
        )

    def test_build_02(self):
        ta = MonthlyTimeAxisBuilder(
            start_year=2019,
            end_year=2020
        ).build()

        self.assertEqual(24, ta.nelem)
        self.assertListEqual(
            [1546326000000000, 1549004400000000, 1551423600000000, 1554102000000000,
             1556694000000000, 1559372400000000, 1561964400000000, 1564642800000000,
             1567321200000000, 1569913200000000, 1572591600000000, 1575183600000000,
             1577862000000000, 1580540400000000, 1583046000000000, 1585724400000000,
             1588316400000000, 1590994800000000, 1593586800000000, 1596265200000000,
             1598943600000000, 1601535600000000, 1604214000000000, 1606806000000000],
            ta.lower_bound[0, :].tolist()
        )
        self.assertListEqual(
            [1548918000000000, 1551337200000000, 1554015600000000, 1556607600000000,
             1559286000000000, 1561878000000000, 1564556400000000, 1567234800000000,
             1569826800000000, 1572505200000000, 1575097200000000, 1577775600000000,
             1580454000000000, 1582959600000000, 1585638000000000, 1588230000000000,
             1590908400000000, 1593500400000000, 1596178800000000, 1598857200000000,
             1601449200000000, 1604127600000000, 1606719600000000, 1609398000000000],
            ta.upper_bound[0, :].tolist()
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
            [1569913200000000, 1572591600000000, 1575183600000000, 1577862000000000,
             1580540400000000, 1583046000000000, 1585724400000000, 1588316400000000],
            ta.lower_bound[0, :].tolist()
        )
        self.assertListEqual(
            [1572505200000000, 1575097200000000, 1577775600000000, 1580454000000000,
             1582959600000000, 1585638000000000, 1588230000000000, 1590908400000000],
            ta.upper_bound[0, :].tolist()
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






