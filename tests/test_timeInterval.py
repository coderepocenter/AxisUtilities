from unittest import TestCase

from axisutilities import Interval


class TestTimeInterval(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._sample_data = []

        # _sample_data[0]: everything is ok:
        cls._sample_data.append([1546326000000000, 1546412400000000, 1546369200000000])

        # _sample_data[1]: upper_bound is smaller than lower_bound
        cls._sample_data.append([1546412400000000, 1546326000000000, 1546369200000000])

        # _sample_data[2]: data_tick is less than lower_bound:
        cls._sample_data.append([1546326000000000, 1546412400000000, 1546325000000000])

        # _sample_data[3]: data_tick is larger than the upper_bound:
        cls._sample_data.append([1546326000000000, 1546412400000000, 1546412500000000])

        # _sample_data[4]: fraction is 0.25
        cls._sample_data.append([1546326000000000, 1546412400000000, 1546347600000000])

        # _sample_data[5]: fraction is 0.0
        cls._sample_data.append([1546326000000000, 1546412400000000, 1546326000000000])

        # _sample_data[6]: fraction is 1.0
        cls._sample_data.append([1546326000000000, 1546412400000000, 1546412400000000])

        import os
        os.environ['TZ'] = "MST"

    def test_creation_00(self):
        lower_bound = self._sample_data[0][0]
        upper_bound = self._sample_data[0][1]
        data_tick = self._sample_data[0][2]

        ti = Interval(lower_bound, upper_bound, data_tick)
        print("Sample TimeInterval: ", ti.asJson())
        expected = '{"lower_bound": "2019-01-01 00:00:00", ' \
                    '"upper_bound": "2019-01-02 00:00:00", ' \
                    '"data_tick": "2019-01-01 12:00:00", ' \
                    '"fraction": 0.5, ' \
                    '"binding": "middle"}'
        self.assertEqual(expected, ti.asJson())

    def test_creation_01(self):
        lower_bound = self._sample_data[1][0]
        upper_bound = self._sample_data[1][1]
        data_tick = self._sample_data[1][2]

        with self.assertRaises(ValueError):
            Interval(lower_bound, upper_bound, data_tick)

    def test_creation_02(self):
        lower_bound = self._sample_data[2][0]
        upper_bound = self._sample_data[2][1]
        data_tick = self._sample_data[2][2]

        with self.assertRaises(ValueError):
            Interval(lower_bound, upper_bound, data_tick)

    def test_creation_03(self):
        lower_bound = self._sample_data[3][0]
        upper_bound = self._sample_data[3][1]
        data_tick = self._sample_data[3][2]

        with self.assertRaises(ValueError):
            Interval(lower_bound, upper_bound, data_tick)

    def test_creation_04(self):
        lower_bound = self._sample_data[4][0]
        upper_bound = self._sample_data[4][1]
        data_tick = self._sample_data[4][2]

        ti = Interval(lower_bound, upper_bound, data_tick)
        print("Sample TimeInterval: ", ti.asJson())
        expected = '{"lower_bound": "2019-01-01 00:00:00", ' \
                    '"upper_bound": "2019-01-02 00:00:00", ' \
                    '"data_tick": "2019-01-01 06:00:00", ' \
                    '"fraction": 0.25, ' \
                    '"binding": "custom_fraction"}'
        self.assertEqual(expected, ti.asJson())

    def test_creation_05(self):
        lower_bound = self._sample_data[5][0]
        upper_bound = self._sample_data[5][1]
        data_tick = self._sample_data[5][2]

        ti = Interval(lower_bound, upper_bound, data_tick)
        print("Sample TimeInterval: ", ti.asJson())
        expected = '{"lower_bound": "2019-01-01 00:00:00", ' \
                    '"upper_bound": "2019-01-02 00:00:00", ' \
                    '"data_tick": "2019-01-01 00:00:00", ' \
                    '"fraction": 0.0, ' \
                    '"binding": "beginning"}'
        self.assertEqual(expected, ti.asJson())

    def test_creation_06(self):
        lower_bound = self._sample_data[6][0]
        upper_bound = self._sample_data[6][1]
        data_tick = self._sample_data[6][2]

        ti = Interval(lower_bound, upper_bound, data_tick)
        print("Sample TimeInterval: ", ti.asJson())
        expected = '{"lower_bound": "2019-01-01 00:00:00", ' \
                    '"upper_bound": "2019-01-02 00:00:00", ' \
                    '"data_tick": "2019-01-02 00:00:00", ' \
                    '"fraction": 1.0, ' \
                    '"binding": "end"}'
        self.assertEqual(expected, ti.asJson())
