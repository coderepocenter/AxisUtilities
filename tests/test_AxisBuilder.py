from datetime import datetime, timedelta, date
from unittest import TestCase

from axisutilities import FixedIntervalAxisBuilder, IntervalBaseAxisBuilder
from axisutilities.axisbuilder import RollingWindowAxisBuilder
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class TestIntervalBaseAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_build_00(self):
        axis = IntervalBaseAxisBuilder()\
            .set_start(0)\
            .set_end(7*24)\
            .set_interval(24)\
            .build()

        self.assertListEqual(
            [i*24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i*24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        self.assertEqual(0.5, axis.fraction[0, 0], 1)

    def test_build_01(self):
        axis = IntervalBaseAxisBuilder(
            start=0,
            end=7*24,
            interval=24
        ).build()

        self.assertListEqual(
            [i*24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i*24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        self.assertEqual(0.5, axis.fraction[0, 0], 1)

    def test_build_02(self):
        axis = IntervalBaseAxisBuilder(
            start=0,
            end=7 * 24,
            interval=24,
            fraction=1.0/6.0
        ).build()

        self.assertListEqual(
            [i * 24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i * 24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        self.assertEqual(1/6, axis.fraction[0, 0], 3)

    def test_build_03(self):
        axis = IntervalBaseAxisBuilder(
            start=0,
            end=7*24,
            interval=24,
            fraction=[0, 0, 0, 0.5, 1, 1, 1]
        ).build()

        self.assertListEqual(
            [i*24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i*24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        for e in zip([0, 0, 0, 0.5, 1, 1, 1], axis.fraction.flatten().tolist()):
            self.assertEqual(e[0] * 1.0, e[1] * 1.0, 1)

    def test_build_04(self):
        axis = IntervalBaseAxisBuilder(
            start=0,
            end=7*24,
            interval=[3*24, 24, 3*24]
        ).build()

        self.assertEqual(3, axis.nelem)
        self.assertListEqual(
            [0, 72, 96],
            axis.lower_bound.flatten().tolist()
        )
        self.assertListEqual(
            [72, 96, 168],
            axis.upper_bound.flatten().tolist()
        )


class TestFixedIntervalAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_build_00(self):
        start = int(datetime.strptime(date(2019, 1, 1).strftime("%c"), "%c").timestamp() * SECONDS_TO_MICROSECONDS_FACTOR)
        end = int(datetime.strptime(date(2019, 1, 8).strftime("%c"), "%c").timestamp() * SECONDS_TO_MICROSECONDS_FACTOR)
        interval = int(timedelta(days=1).total_seconds() * SECONDS_TO_MICROSECONDS_FACTOR)
        ta = FixedIntervalAxisBuilder()\
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

    def test_build_01(self):
        axis = FixedIntervalAxisBuilder(
            start=0,
            end=7*24,
            n_interval=7
        ).build()

        self.assertListEqual(
            [i * 24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i * 24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        self.assertEqual(0.5, axis.fraction[0, 0], 1)

    def test_build_02(self):
        axis = FixedIntervalAxisBuilder(
            start=0,
            end=7*24,
            interval=24
        ).build()

        self.assertListEqual(
            [i * 24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i * 24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        self.assertEqual(0.5, axis.fraction[0, 0], 1)

    def test_build_03(self):
        axis = FixedIntervalAxisBuilder(
            end=7*24,
            interval=24,
            n_interval=7
        ).build()

        self.assertListEqual(
            [i * 24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i * 24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        self.assertEqual(0.5, axis.fraction[0, 0], 1)

    def test_build_04(self):
        axis = FixedIntervalAxisBuilder(
            start=0,
            interval=24,
            n_interval=7
        ).build()

        self.assertListEqual(
            [i * 24 for i in range(7)],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [i * 24 + 24 for i in range(7)],
            axis.upper_bound.flatten().tolist()
        )

        self.assertEqual(0.5, axis.fraction[0, 0], 1)


class TestRollingWindowAxisBuilder(TestCase):
    def test_build_00(self):
        axis = RollingWindowAxisBuilder()\
            .set_start(0)\
            .set_base(24)\
            .set_window_size(3)\
            .set_end(7*24)\
            .build()

        self.assertEqual(5, axis.nelem)
        self.assertListEqual(
            [0, 24, 48, 72, 96],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [72, 96, 120, 144, 168],
            axis.upper_bound.flatten().tolist()
        )

    def test_build_01(self):
        axis = RollingWindowAxisBuilder(
            start=0,
            end=7*24,
            base=24,
            window_size=3
        ).build()

        self.assertEqual(5, axis.nelem)
        self.assertListEqual(
            [0, 24, 48, 72, 96],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [72, 96, 120, 144, 168],
            axis.upper_bound.flatten().tolist()
        )

    def test_build_02(self):
        axis = RollingWindowAxisBuilder(
            start=0,
            base=24,
            window_size=3,
            n_window=5
        ).build()

        self.assertEqual(5, axis.nelem)
        self.assertListEqual(
            [0, 24, 48, 72, 96],
            axis.lower_bound.flatten().tolist()
        )

        self.assertListEqual(
            [72, 96, 120, 144, 168],
            axis.upper_bound.flatten().tolist()
        )

    def test_build_03(self):
        with self.assertRaises(ValueError):
            RollingWindowAxisBuilder(
                start=0,
                base=24,
                window_size=3,
                n_window=5,
                end=7*24  # Both n_window and end are provided.
            ).build()

    def test_build_04(self):
        with self.assertRaises(ValueError):
            RollingWindowAxisBuilder(
                start=7*24,  # start is after end
                end=0,
                base=24,
                window_size=3
            ).build()

    def test_build_05(self):
        with self.assertRaises(ValueError):
            RollingWindowAxisBuilder(
                start=0,
                end=7*24,
                base=24,
                window_size=4  # even window_size
            ).build()

    def test_build_06(self):
        with self.assertRaises(ValueError):
            RollingWindowAxisBuilder(
                start=0,
                end=7*24,
                base=24,
                window_size=-3  # negative window_size
            ).build()

    def test_build_07(self):
        with self.assertRaises(TypeError):
            RollingWindowAxisBuilder(
                start=0,
                end=7*24,
                base=24,
                window_size='I try to be an integral'  # Non-castable to int
            ).build()









