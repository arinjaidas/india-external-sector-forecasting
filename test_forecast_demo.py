import unittest
import numpy as np
import pandas as pd
from forecast_demo import COMPONENTS, CA_COMPONENTS, CAPITAL, METHODS, synthetic_data, validate, reconcile, forecast, rolling_predictions, select_method


class ForecastTests(unittest.TestCase):
    def test_seasonal_naive_exact_repetition(self):
        data = synthetic_data(); pred = forecast(data, 'seasonal_naive', 8)
        np.testing.assert_allclose(pred[COMPONENTS].to_numpy(), np.tile(data.iloc[-4:].to_numpy(), (2, 1)))

    def test_all_methods_preserve_accounting(self):
        for method in METHODS:
            p = forecast(synthetic_data(), method)
            np.testing.assert_allclose(p.current_account, p[CA_COMPONENTS].sum(axis=1))
            np.testing.assert_allclose(p.reserve_transactions, p.current_account + p[CAPITAL].sum(axis=1))

    def test_training_prefix_unchanged_by_future(self):
        one = synthetic_data(); two = one.copy(); two.iloc[60:] += 100000
        a = rolling_predictions(one, [48]); b = rolling_predictions(two, [48])
        pd.testing.assert_frame_equal(a, b)

    def test_forward_index(self):
        data = synthetic_data(); p = forecast(data, 'ar1')
        self.assertEqual(p.index[0], data.index[-1] + 1)

    def test_missing_quarter_rejected(self):
        with self.assertRaises(ValueError): validate(synthetic_data().drop(index='2001Q1'))

    def test_nonfinite_rejected(self):
        data = synthetic_data(); data.iloc[0, 0] = np.inf
        with self.assertRaises(ValueError): validate(data)

    def test_constant_series_are_supported(self):
        data = synthetic_data(); data[:] = np.arange(7)
        for method in METHODS:
            p = forecast(data, method)
            np.testing.assert_allclose(p[COMPONENTS], np.tile(np.arange(7), (4, 1)), atol=1e-10)

    def test_selection_safeguard(self):
        rows = [{'method': m, 'series': 'current_account', 'error': e, 'ca_training_seasonal_scale': 1}
                for m, e in [('seasonal_naive', 100), ('ar1', 99), ('ridge_var', 110)]]
        selected, _ = select_method(pd.DataFrame(rows))
        self.assertEqual(selected, 'seasonal_naive')
        rows[1]['error'] = 90
        self.assertEqual(select_method(pd.DataFrame(rows))[0], 'ar1')

    def test_invalid_origin(self):
        with self.assertRaises(ValueError): rolling_predictions(synthetic_data(), [103], 4)

    def test_future_observations_cannot_affect_model_choice(self):
        data = synthetic_data(); altered = data.copy(); altered.iloc[72:] *= 20
        a = rolling_predictions(data, list(range(48, 69, 4)))
        b = rolling_predictions(altered, list(range(48, 69, 4)))
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(select_method(a)[0], select_method(b)[0])


if __name__ == '__main__': unittest.main()
