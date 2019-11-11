from datetime import datetime, timedelta
from unittest import TestCase

from axisutilities import FixedIntervalAxisBuilder
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class TestIntervalBaseAxisBuilder(TestCase):
    pass


class TestFixedIntervalTimeAxisBuilder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_creation_01(self):
        start = int(datetime(2019, 1, 1).timestamp() * SECONDS_TO_MICROSECONDS_FACTOR)
        end = int(datetime(2019, 1, 8).timestamp() * SECONDS_TO_MICROSECONDS_FACTOR)
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