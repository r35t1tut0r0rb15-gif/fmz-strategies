"""DI 14 crossings with ADX (14 / 14) over 25, 4-hour bars: DI+ crossing over DI- goes long, under goes short, each with a 1 % stop and 2 % target from the entry price; reversing.
Port of FMZ strategy #482424 "动量趋势跟踪指标DMIADX交叉策略-Momentum-Trend-Following-DMIADX-Crossover-Strategy" (DMI + ADX Strategy).

FMZ source id: 482424

Source
    https://www.fmz.com/strategy/482424 (PineScript v6, FMZ last modified 2025-02-18 13:47:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-170), DMI 14, ADX smoothing 14, threshold 25; stop 1 %, target 2 % of strategy.position_avg_price; 250 % of equity
    crossover(di+, di-) and adx > 25 -> entry Long;  crossunder and adx > 25 -> entry Short;  long: exit(stop = avg x 0.99, limit = avg x 1.02);  short: exit(stop = avg x 1.01, limit = avg x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent from the position's average price while it is held: scalar fractions of the
      entry fill, active from the fill (as #440797). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The 250 % of equity size is
      sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill.
    2 generic: PASS, DI crossings with an ADX filter and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482424_di14_cross_adx25_pct_bracket_reversal"
FAMILY = "adx_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [25.0, 20.0],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"adx_threshold": 25.0, "tp_pct": 0.02, "sl_pct": 0.01, "dmi_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    plus, minus, adx = _dmi(bars_df, int(p["dmi_length"]))
    strong = adx > float(p["adx_threshold"])
    le = (plus > minus) & (plus.shift(1) <= minus.shift(1)) & strong
    se = (plus < minus) & (plus.shift(1) >= minus.shift(1)) & strong
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
