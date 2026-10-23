"""An unsmoothed stochastic of RSI 14 over 14 bars with an SMA 9 / 21 spread and the session VWAP of hlc3, 1-minute bars: the stochastic crossing over 30 with the fast SMA above the slow one and the close under the VWAP goes long; crossing under 70 with the fast SMA below and the close over the VWAP goes short; reversing.
Port of FMZ strategy #426336 "Stochastic RSI Trading Strategy" (Stochastic RSI Strategy).

FMZ source id: 426336

Source
    https://www.fmz.com/strategy/426336 (PineScript v4, FMZ last modified 2023-09-11 11:57:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 97-130), RSI 14 of close, stochastic over 14 (K / D inputs 3 / 3; k is not smoothed); SMA 9 / 21; vwap(hlc3)
    k = (rsi - lowest(rsi, 14)) / (highest(rsi, 14) - lowest(rsi, 14)) x 100
    crossover(k, 30) and sma(9) - sma(21) > 0 and close < vwap(hlc3) -> entry Long;  crossunder(k, 70) and spread < 0 and close > vwap -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * k is the raw stochastic of the RSI as written (smoothK is never used; d feeds nothing). A flat RSI
      window (highest = lowest) gives na. vwap(hlc3) is anchored at the broker-day start (17:00
      America/New_York), as #363564. The commented exits are not used. REVERSAL INTENDED. No sizing code.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic-RSI turns with an SMA spread and VWAP side filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwap(hlc3), anchored at the broker-day start; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VWAP anchored at the broker-day start (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426336_raw_stoch_rsi14_sma9_21_spread_session_vwap_side_reversal"
FAMILY = "stochastic_rsi"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "os_level": [30.0, 20.0],
}
DEFAULT_PARAMS = {"length": 14, "os_level": 30.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["length"])
    r = _rsi(c, n)
    hr, lr = r.rolling(n).max(), r.rolling(n).min()
    k = (r - lr) / (hr - lr).replace(0.0, np.nan) * 100
    spread = c.rolling(9).mean() - c.rolling(21).mean()
    day = broker_day(c.index)
    pv = (v * (h + lo + c) / 3).groupby(day).cumsum()
    cvol = v.groupby(day).cumsum()
    vwap = pd.Series((pv / cvol.where(cvol != 0)).to_numpy(), index=c.index)
    os_, ob_ = float(p["os_level"]), 100.0 - float(p["os_level"])
    le = (k > os_) & (k.shift(1) <= os_) & (spread > 0) & (c < vwap)
    se = (k < ob_) & (k.shift(1) >= ob_) & (spread < 0) & (c > vwap) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
