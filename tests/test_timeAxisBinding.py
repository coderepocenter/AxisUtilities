from unittest import TestCase

from axisutilities import AxisBinding


class TestTimeAxisBinding(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import os
        os.environ['TZ'] = 'MST'

    def test_repr_01(self):
        self.assertEqual("beginning", repr(AxisBinding.BEGINNING))

    def test_repr_02(self):
        self.assertEqual("end", repr(AxisBinding.END))

    def test_repr_03(self):
        self.assertEqual("middle", repr(AxisBinding.MIDDLE))

    def test_repr_04(self):
        self.assertEqual("custom_fraction", repr(AxisBinding.CUSTOM_FRACTION))

    def test_valueOf_01(self):
        self.assertEqual(
            AxisBinding.BEGINNING,
            AxisBinding.valueOf("beGiNnIng")
        )

    def test_valueOf_02(self):
        with self.assertRaises(ValueError):
            AxisBinding.valueOf("None Existing")

    def test_valueOf_03(self):
        self.assertEqual(
            AxisBinding.BEGINNING,
            AxisBinding.valueOf(AxisBinding.BEGINNING)
        )

    def test_valueOf_04(self):
        with self.assertRaises(TypeError):
            AxisBinding.valueOf({})

    def test_valueOf_05(self):
        self.assertEqual(AxisBinding.BEGINNING, AxisBinding.valueOf(0))

    def test_valueOf_06(self):
        self.assertEqual(AxisBinding.END, AxisBinding.valueOf(1.0))

    def test_valueOf_07(self):
        self.assertEqual(AxisBinding.MIDDLE, AxisBinding.valueOf(0.5))

    def test_valueOf_08(self):
        self.assertEqual(AxisBinding.CUSTOM_FRACTION, AxisBinding.valueOf(0.2))

    def test_valueOf_09(self):
        with self.assertRaises(ValueError):
            AxisBinding.valueOf(10)

    def test_fraction_01(self):
        self.assertEqual(0.0, AxisBinding.BEGINNING.fraction())

    def test_fraction_02(self):
        self.assertEqual(1.0, AxisBinding.END.fraction())

    def test_fraction_03(self):
        self.assertEqual(0.5, AxisBinding.MIDDLE.fraction())

    def test_fraction_04(self):
        self.assertEqual(None, AxisBinding.CUSTOM_FRACTION.fraction())






