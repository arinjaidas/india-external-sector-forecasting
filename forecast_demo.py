"""Synthetic accounting-coherent forecast demonstration, newly implemented in 2026.

The original MAAKRO research package is separate. Forecast selection uses an
early validation period; a later test period is evaluated with that choice frozen.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CA_COMPONENTS = ['goods', 'services', 'primary_income', 'secondary_income']
CAPITAL = ['fdi', 'portfolio', 'other_inflows']
COMPONENTS = CA_COMPONENTS + CAPITAL
METHODS = ['seasonal_naive', 'ar1', 'ridge_var']


def validate(frame):
    data = frame.copy()
    data.index = pd.PeriodIndex(data.index, freq='Q')
    if not set(COMPONENTS).issubset(data) or len(data) < 12:
        raise ValueError('At least twelve quarters and all seven components are needed.')
    if data.index.has_duplicates or not data.index.equals(pd.period_range(data.index[0], periods=len(data), freq='Q')):
        raise ValueError('Quarters must be unique, increasing and consecutive.')
    data = data[COMPONENTS].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(data.to_numpy()).all():
        raise ValueError('All components must be finite and complete.')
    return data


def reconcile(components):
    out = components[COMPONENTS].copy()
    out['current_account'] = out[CA_COMPONENTS].sum(axis=1)
    out['net_inflows'] = out[CAPITAL].sum(axis=1)
    out['reserve_transactions'] = out.current_account + out.net_inflows
    return out


def forecast(frame, method, horizon=4, ridge_penalty=10.0):
    data = validate(frame)
    if method not in METHODS or not isinstance(horizon, int) or horizon < 1:
        raise ValueError('Choose a supported method and positive integer horizon.')
    values = data.to_numpy()
    if method == 'seasonal_naive':
        predictions = np.array([values[-4 + (h % 4)] for h in range(horizon)])
    elif method == 'ar1':
        coefficients = []
        for j in range(values.shape[1]):
            x = np.column_stack([np.ones(len(values) - 1), values[:-1, j]])
            coefficients.append(np.linalg.lstsq(x, values[1:, j], rcond=None)[0])
        coefficients = np.asarray(coefficients)
        last = values[-1].copy(); predictions = []
        for _ in range(horizon):
            last = coefficients[:, 0] + coefficients[:, 1] * last
            predictions.append(last.copy())
        predictions = np.asarray(predictions)
    else:
        if not np.isfinite(ridge_penalty) or ridge_penalty <= 0:
            raise ValueError('Ridge penalty must be positive and finite.')
        center = values.mean(axis=0)
        scale = values.std(axis=0, ddof=1)
        scale[scale < 1e-12] = 1
        z = (values - center) / scale
        x = np.column_stack([np.ones(len(z) - 1), z[:-1]])
        penalty = np.eye(x.shape[1]) * ridge_penalty; penalty[0, 0] = 0
        beta = np.linalg.solve(x.T @ x + penalty, x.T @ z[1:])
        last = z[-1].copy(); predictions = []
        for _ in range(horizon):
            last = np.r_[1, last] @ beta
            predictions.append(last * scale + center)
        predictions = np.asarray(predictions)
    future = pd.period_range(data.index[-1] + 1, periods=horizon, freq='Q')
    return reconcile(pd.DataFrame(predictions, columns=COMPONENTS, index=future))


def rolling_predictions(frame, origins, horizon=4):
    data = validate(frame)
    truth = reconcile(data)
    rows = []
    for origin in origins:
        if not isinstance(origin, (int, np.integer)) or origin < 12 or origin + horizon > len(data):
            raise ValueError('Each origin needs training history and a complete evaluation horizon.')
        training = data.iloc[:origin]
        scale = truth.current_account.iloc[:origin].diff(4).abs().dropna().mean()
        for method in METHODS:
            pred = forecast(training, method, horizon)
            for h in range(horizon):
                for series in ['current_account', 'reserve_transactions']:
                    actual = float(truth[series].iloc[origin + h])
                    predicted = float(pred[series].iloc[h])
                    rows.append({'origin': str(data.index[origin - 1]), 'target': str(pred.index[h]),
                                 'horizon': h + 1, 'method': method, 'series': series,
                                 'actual': actual, 'prediction': predicted, 'error': actual - predicted,
                                 'ca_training_seasonal_scale': float(scale)})
    return pd.DataFrame(rows)


def metrics(predictions):
    rows = []
    for (method, series), part in predictions.groupby(['method', 'series']):
        row = {'method': method, 'series': series, 'forecasts': len(part),
               'mae': float(part.error.abs().mean()), 'rmse': float(np.sqrt(np.mean(part.error ** 2)))}
        if series == 'current_account':
            usable = part.ca_training_seasonal_scale > 1e-12
            row['mase'] = float((part.loc[usable, 'error'].abs() / part.loc[usable, 'ca_training_seasonal_scale']).mean()) if usable.any() else None
        else:
            row['mase'] = None
        rows.append(row)
    return pd.DataFrame(rows)


def select_method(validation_predictions, improvement_required=.02):
    if not 0 <= improvement_required < 1:
        raise ValueError('Improvement threshold must lie in [0, 1).')
    scores = metrics(validation_predictions)
    ca = scores.loc[scores.series == 'current_account'].set_index('method').mae
    if set(ca.index) != set(METHODS):
        raise ValueError('Validation must contain all candidate methods.')
    candidate = ca.idxmin()
    chosen = candidate if ca[candidate] < ca['seasonal_naive'] * (1 - improvement_required) else 'seasonal_naive'
    return chosen, scores


def synthetic_data(seed=20261019, n=104):
    rng = np.random.default_rng(seed)
    means = np.array([-26000, 15500, -4500, 9000, 7000, 2000, 1000])
    seasonal = np.array([1.0, -.5, .3, -.8])
    z = np.zeros((n, 7))
    for t in range(1, n):
        z[t] = .65 * z[t - 1] + rng.normal(0, [1300, 750, 250, 500, 600, 1800, 1000])
    values = means + z + seasonal[np.arange(n) % 4, None] * [1800, 600, 120, 500, 400, 500, 200]
    return pd.DataFrame(values, index=pd.period_range('2000Q1', periods=n, freq='Q'), columns=COMPONENTS)


def run(frame, output, synthetic=False, min_train=48, split=72, horizon=4):
    data = validate(frame)
    if not 12 <= min_train <= split - horizon or split + horizon > len(data):
        raise ValueError('Need disjoint training, validation and later test periods.')
    validation_origins = list(range(min_train, split - horizon + 1, horizon))
    test_origins = list(range(split, len(data) - horizon + 1, horizon))
    val = rolling_predictions(data, validation_origins, horizon)
    selected, validation_metrics = select_method(val)
    test = rolling_predictions(data, test_origins, horizon)
    test_metrics = metrics(test)
    test_metrics['frozen_selected_method'] = test_metrics.method == selected
    out = Path(output); out.mkdir(parents=True, exist_ok=True)
    reconcile(data).to_csv(out / 'synthetic_history.csv' if synthetic else out / 'accounting_history.csv', index_label='quarter')
    val.to_csv(out / 'validation_predictions.csv', index=False)
    validation_metrics.to_csv(out / 'validation_metrics.csv', index=False)
    test.to_csv(out / 'test_predictions.csv', index=False)
    test_metrics.to_csv(out / 'test_metrics.csv', index=False)
    future = forecast(data, selected, horizon)
    future.to_csv(out / 'forecast_components.csv', index_label='quarter')
    chosen = test[(test.method == selected) & (test.series == 'current_account')].copy()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    x = pd.PeriodIndex(chosen.target, freq='Q').to_timestamp()
    ax.plot(x, chosen.actual, label='Observed synthetic current account', color='#18354a')
    ax.plot(x, chosen.prediction, label=f'Frozen selection: {selected}', color='#238c83')
    ax.set(title='SYNTHETIC LATER TEST PERIOD', ylabel='Illustrative USD million', xlabel='Quarter')
    ax.legend(fontsize=8); ax.grid(alpha=.2); fig.tight_layout()
    fig.savefig(out / 'forecast_evaluation.svg'); plt.close(fig)
    meta = {'synthetic': synthetic, 'rows': len(data), 'seed': 20261019, 'horizon': horizon,
            'min_train': min_train, 'validation_origin_count': len(validation_origins), 'test_origin_count': len(test_origins),
            'test_start': str(data.index[split]), 'selected_method': selected,
            'selection': 'Current-account validation MAE; requires 2 percent improvement over seasonal naive. Choice frozen before later test.',
            'ridge_penalty': 10.0, 'source_vintage': 'Synthetic data; real-data use is current-vintage retrospective unless true historical vintages are supplied.',
            'scope': 'New public implementation, not the original MAAKRO forecasting package.',
            'interpretation': 'Synthetic forecasting exercise; no historical India forecast accuracy or real-time track record is claimed.'}
    (out / 'run_metadata.json').write_text(json.dumps(meta, indent=2))
    return meta


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo', action='store_true'); group.add_argument('--data', type=Path)
    p.add_argument('--output', default='demo_output'); args = p.parse_args()
    source = synthetic_data() if args.demo else pd.read_csv(args.data, index_col='quarter')
    print(json.dumps(run(source, args.output, args.demo), indent=2))
