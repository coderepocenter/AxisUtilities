from datetime import date
from unittest import TestCase, skip

import numpy as np

from axisutilities import Axis, AxisConverter, DailyTimeAxisBuilder, WeeklyTimeAxisBuilder, \
    RollingWindowTimeAxisBuilder, MonthlyTimeAxisBuilder


class TestTimeAxisConverter(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_get_coverage_01(self):
        from_axis = Axis(
            lower_bound=np.arange(0, 7)*24,
            upper_bound=np.arange(1, 8)*24,
            fraction=0.5
        )

        to_axis = Axis(
            lower_bound=[0],
            upper_bound=[168],
            data_ticks=[84]
        )

        row_idx, col_idx, weights = AxisConverter._get_coverage(
            from_axis.lower_bound, from_axis.upper_bound,
            to_axis.lower_bound, to_axis.upper_bound
        )

        self.assertListEqual([0]*7, row_idx)
        self.assertListEqual(list(range(7)), col_idx)
        self.assertListEqual([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], weights)

    def test_get_coverage_02(self):
        from_axis = Axis(
            lower_bound=[0],
            upper_bound=[168],
            data_ticks=[84]
        )

        to_axis = Axis(
            lower_bound=np.arange(0, 7) * 24,
            upper_bound=np.arange(1, 8) * 24,
            fraction=0.5
        )

        row_idx, col_idx, coverageWeight = AxisConverter._get_coverage(
            from_axis.lower_bound, from_axis.upper_bound,
            to_axis.lower_bound, to_axis.upper_bound
        )
        self.assertListEqual(list(range(7)), row_idx)
        self.assertListEqual([0]*7, col_idx)
        self.assertListEqual([1.0/7.0, 1.0/7.0, 1.0/7.0, 1.0/7.0, 1.0/7.0, 1.0/7.0, 1.0/7.0], coverageWeight)

    def test_get_coverage_03(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        row_idx, col_idx, weights = AxisConverter._get_coverage(
            from_axis.lower_bound, from_axis.upper_bound,
            to_axis.lower_bound, to_axis.upper_bound
        )

        self.assertListEqual([0] * 7, row_idx)
        self.assertListEqual(list(range(7)), col_idx)
        self.assertListEqual([1.0] * 7, weights)

    def test_creation_01(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

    def test_average_01(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = [1, 2, 3, 4, 5, 6, 7]

        to_data = tc.average(from_data)

        self.assertAlmostEqual(4.0, to_data[0, 0], 0)

    def test_average_02(self):
        from_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        to_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = [4.0]

        to_data = tc.average(from_data)

        self.assertEqual((tc.to_nelem, 1), to_data.shape)

        for e in to_data:
            self.assertAlmostEqual(4.0, e[0], 0)

    def test_average_03(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_end_date(date(2019, 1, 8)) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.asarray([1, 2, 3, 4, 5, 6, 7])

        to_data = tc.average(from_data)

        self.assertAlmostEqual(4.0, to_data[0, 0], 0)

    def test_average_04(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(14) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(2) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))

        to_data = tc.average(from_data)

        self.assertAlmostEqual(4.0, to_data[0, 0], 0)
        self.assertAlmostEqual(11.0, to_data[1, 0], 0)

    def test_average_05(self):
        from_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(2) \
            .build()

        to_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(14) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = [4.0, 11]

        to_data = tc.average(from_data)

        expected = [4] * 7 + [11] * 7
        self.assertListEqual(expected, to_data.flatten().tolist())

    def test_average_06(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(14) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(2) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 0)

        to_data = tc.average(from_data)

        self.assertEqual((2, 3, 4), to_data.shape)

        self.assertListEqual(
            [4] * 12,
            np.round(to_data[0, :, :].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

        self.assertListEqual(
            [11] * 12,
            np.round(to_data[1, :, :].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

    def test_average_07(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(14) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(2) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14))

        to_data = tc.average(from_data, time_dimension=2)

        self.assertEqual((3, 4, 2), to_data.shape)

        self.assertListEqual(
            [4] * 12,
            np.round(to_data[:, :, 0].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

        self.assertListEqual(
            [11] * 12,
            np.round(to_data[:, :, 1].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

    def test_average_08(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(14) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(2) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 1)

        to_data = tc.average(from_data, time_dimension=1)

        self.assertEqual((3, 2, 4), to_data.shape)

        self.assertListEqual(
            [4] * 12,
            np.round(to_data[:, 0, :].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

        self.assertListEqual(
            [11] * 12,
            np.round(to_data[:, 1, :].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

    def test_average_09(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 1).tolist()

        to_data = tc.average(from_data, time_dimension=1)

        self.assertEqual((3, 2, 4), to_data.shape)

        self.assertListEqual(
            [4] * 12,
            np.round(to_data[:, 0, :].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

        self.assertListEqual(
            [11] * 12,
            np.round(to_data[:, 1, :].reshape((-1, 1))).astype(np.int).flatten().tolist()
        )

    def test_average_10(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=3
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))

        to_data = tc.average(from_data)

        self.assertAlmostEqual(4.0, to_data[0, 0], 0)
        self.assertAlmostEqual(11.0, to_data[1, 0], 0)
        self.assertTrue(np.isnan(to_data[2, 0]))

    def test_average_11(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = RollingWindowTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))

        to_data = tc.average(from_data)
        self.assertEqual(8, to_data.size)

        for idx in range(8):
            self.assertAlmostEqual(idx+4, to_data[idx, 0], 0)

    def test_average_12(self):
        from_axis = DailyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(14) \
            .build()

        to_axis = WeeklyTimeAxisBuilder()\
            .set_start_date(date(2019, 1, 1)) \
            .set_n_interval(2) \
            .build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))
        from_data[2] = np.nan

        to_data = tc.average(from_data)

        self.assertAlmostEqual(4.167, to_data[0, 0], 3)
        self.assertAlmostEqual(11.0, to_data[1, 0], 3)

    def test_min_01(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))

        to_data = tc.min(from_data)

        self.assertAlmostEqual(1.0, to_data[0, 0], 0)
        self.assertAlmostEqual(8.0, to_data[1, 0], 0)

    def test_min_02(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 0).tolist()

        to_data = tc.min(from_data)

        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") - to_data[0].round() == 0.0
            )
        )
        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") * 8 - to_data[1].round() == 0.0
            )
        )

    def test_min_03(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 1).tolist()

        to_data = tc.min(from_data, time_dimension=1)

        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") - to_data[:, 0, :].round() == 0.0
            )
        )
        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") * 8 - to_data[:, 1, :].round() == 0.0
            )
        )

    def test_min_04(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = RollingWindowTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 1).tolist()

        to_data = tc.min(from_data, time_dimension=1)

        for i in range(tc.to_nelem):
            self.assertTrue(
                np.all(
                    np.ones((3, 4), dtype="int") * (1 + i) - to_data[:, i, :].round() == 0.0
                )
            )

    def test_min_05(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=3
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))

        to_data = tc.min(from_data)

        self.assertAlmostEqual(1.0, to_data[0, 0], 0)
        self.assertAlmostEqual(8.0, to_data[1, 0], 0)
        self.assertTrue(np.isnan(to_data[2, 0]))

    def test_max_01(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))

        to_data = tc.max(from_data)

        self.assertAlmostEqual(7.0, to_data[0, 0], 0)
        self.assertAlmostEqual(14.0, to_data[1, 0], 0)

    def test_max_02(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 0).tolist()

        to_data = tc.max(from_data)

        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") * 7 - to_data[0].round() == 0.0
            )
        )
        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") * 14 - to_data[1].round() == 0.0
            )
        )

    def test_max_03(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=2
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 1).tolist()

        to_data = tc.max(from_data, time_dimension=1)

        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") * 7 - to_data[:, 0, :].round() == 0.0
            )
        )
        self.assertTrue(
            np.all(
                np.ones((3, 4), dtype="int") * 14 - to_data[:, 1, :].round() == 0.0
            )
        )

    def test_max_04(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = RollingWindowTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            end_date=date(2019, 1, 15),
            window_size=7
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.moveaxis(np.asarray(list(range(1, 15)) * 12).reshape((3, 4, 14)), 2, 1).tolist()

        to_data = tc.max(from_data, time_dimension=1)

        for i in range(tc.to_nelem):
            self.assertTrue(
                np.all(
                    np.ones((3, 4), dtype="int") * (7+i) - to_data[:, i, :].round() == 0.0
                )
            )

    def test_max_05(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=14
        ).build()

        to_axis = WeeklyTimeAxisBuilder(
            start_date=date(2019, 1, 1),
            n_interval=3
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = list(range(1, 15))

        to_data = tc.max(from_data)

        self.assertAlmostEqual(7.0, to_data[0, 0], 0)
        self.assertAlmostEqual(14.0, to_data[1, 0], 0)
        self.assertTrue(np.isnan(to_data[2, 0]))


    @skip
    def test_speed_01(self):
        from_axis = DailyTimeAxisBuilder(
            start_date=date(2000, 1, 1),
            end_date=date(2020, 1, 1)
        ).build()

        to_axis = MonthlyTimeAxisBuilder(
            start_year=2000,
            end_year=2019
        ).build()

        tc = AxisConverter(from_axis=from_axis, to_axis=to_axis)

        from_data = np.random.random((from_axis.nelem, 100, 100))

        import time
        start = time.time()
        for i in range(1):
            tc.min(from_data)
        end = time.time()

        print(f"Took: %f [s]", end -start)

        import time
        start = time.time()
        for i in range(1):
            tc.min(from_data)
        end = time.time()

        print(f"Took: %f [s]", end - start)


