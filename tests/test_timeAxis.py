from datetime import date
from unittest import TestCase

from axisutilities import Axis, DailyTimeAxisBuilder


class TestTimeAxis(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    @classmethod
    def setUpClass(cls) -> None:
        cls._sample_date = []

        # _sample_date[0]: known data_ticks:

        cls._sample_date.append(
            {
                "lower_bound": [1546326000000000, 1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000],
                "upper_bound": [1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000],
                "data_ticks": [1546369200000000, 1546455600000000, 1546542000000000, 1546628400000000, 1546714800000000, 1546801200000000]
            }
        )

    def test_creation_01(self):
        lower_bound = self._sample_date[0]["lower_bound"]
        upper_bound = self._sample_date[0]["upper_bound"]
        data_ticks = self._sample_date[0]["data_ticks"]

        ta = Axis(lower_bound, upper_bound, data_ticks=data_ticks)
        print("Sample TimeAxis Initialized: ", ta.asJson())
        expected = '{"nelem": 6, ' \
                    '"lower_bound": [1546326000000000, 1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000], ' \
                    '"upper_bound": [1546412400000000, 1546498800000000, 1546585200000000, 1546671600000000, 1546758000000000, 1546844400000000], ' \
                    '"data_ticks": [1546369200000000, 1546455600000000, 1546542000000000, 1546628400000000, 1546714800000000, 1546801200000000], ' \
                    '"fraction": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5], ' \
                    '"binding": "middle"}'
        self.assertEqual(expected, ta.asJson())
        self.assertListEqual(lower_bound, ta.lower_bound.tolist()[0])
        self.assertListEqual(upper_bound, ta.upper_bound.tolist()[0])
        self.assertListEqual(data_ticks, ta.data_ticks.tolist()[0])
        expected = [(data_ticks[i] - lower_bound[i])/(upper_bound[i] - lower_bound[i]) for i in range(len(lower_bound))]
        self.assertListEqual(expected, ta.fraction.tolist()[0])
        self.assertEqual(len(lower_bound), ta.nelem)
        self.assertEqual("2019-01-01 12:00:00", ta[0].asDict()["data_tick"])
        self.assertEqual("2019-01-02 12:00:00", ta[1].asDict()["data_tick"])
        self.assertEqual("2019-01-03 12:00:00", ta[2].asDict()["data_tick"])
        self.assertEqual("2019-01-04 12:00:00", ta[3].asDict()["data_tick"])
        self.assertEqual("2019-01-05 12:00:00", ta[4].asDict()["data_tick"])
        self.assertEqual("2019-01-06 12:00:00", ta[5].asDict()["data_tick"])

    def test_builder_01(self):
        self.assertTrue(
            isinstance(
                DailyTimeAxisBuilder(),
                DailyTimeAxisBuilder
            )
        )

    def test_builder_02(self):
        ta = DailyTimeAxisBuilder()\
                .set_start_date(date(2019, 1, 1))\
                .set_end_date(date(2019, 1, 8))\
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
        self.assertEqual(7, ta.nelem)
        self.assertEqual("2019-01-01 12:00:00", ta[0].asDict()["data_tick"])
        self.assertEqual("2019-01-02 12:00:00", ta[1].asDict()["data_tick"])
        self.assertEqual("2019-01-03 12:00:00", ta[2].asDict()["data_tick"])
        self.assertEqual("2019-01-04 12:00:00", ta[3].asDict()["data_tick"])
        self.assertEqual("2019-01-05 12:00:00", ta[4].asDict()["data_tick"])
        self.assertEqual("2019-01-06 12:00:00", ta[5].asDict()["data_tick"])
        self.assertEqual("2019-01-07 12:00:00", ta[6].asDict()["data_tick"])


















