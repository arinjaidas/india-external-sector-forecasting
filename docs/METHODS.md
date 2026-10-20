# Methods

## Component coherence

The four current-account components are goods, services, primary income and secondary income. Their sum defines current account. FDI, portfolio and other inflows define net non-reserve financial inflows. Reserve transactions equal current account plus these inflows under the simplified funding convention. Forecast aggregates are calculated from component forecasts, so the identities hold by construction.

## Candidate forecasts

Seasonal naive repeats the last four component observations. AR1 estimates a separate intercept and lag coefficient for each component. Ridge VAR standardises the seven components using the current training sample and estimates a one-lag system with ridge penalty 10. The intercept is not penalised. Recursive forecasts are transformed back to the original units before aggregation.

## Chronological protocol

The synthetic history has 104 quarters. The first origin follows 48 training observations. Six four-quarter validation blocks end before observation 72. A model replaces seasonal naive only if its validation current-account MAE is at least two percent lower. The selected method is then frozen before eight later four-quarter test blocks. Test outcomes can be used for reporting but not to change that earlier choice.

MAE and RMSE are reported for current account and reserve transactions. Current-account MASE uses each origin's training-sample mean absolute seasonal difference as its denominator. An undefined zero scale is not silently treated as a valid ratio. Final four-quarter point forecasts refit the already selected method on all available history. No calibrated predictive interval is produced.
