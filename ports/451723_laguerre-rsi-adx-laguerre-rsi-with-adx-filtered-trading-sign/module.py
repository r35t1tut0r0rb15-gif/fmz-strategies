"""Laguerre RSI (alpha 0.2) crossings with an ADX 14 filter, daily bars: the Laguerre RSI crossing over 20 with the ADX over 20 goes long, crossing under 80 with the ADX over 20 goes short; reversing.
Port of FMZ strategy #451723 "Laguerre-RSI与ADX滤波交易信号策略-Laguerre-RSI-with-ADX-Filtered-Trading-Signals-Strategy" (Laguerre RSI with Buy/Sell Signals and ADX Filter (LaRSI_ADX Signals)).

FMZ source id: 451723

Source
    https://www.fmz.com/strategy/451723 (PineScript v5, FMZ last modified 2024-05-17 15:01:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-144), Laguerre alpha 0.2 (gamma 0.8); levels 20 / 80; DMI 14 / 14, ADX level 20
    crossover(100 x laRSI, 20) and adx > 20 -> entry Long;  crossunder(100 x laRSI, 80) and adx > 20 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The four Laguerre filters run recursively from 0 (nz), as written; a bar with no up or down
      movement among them gives 0. ta.dmi is Wilder's (rma) DMI / ADX. There is no exit: positions
      end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Laguerre RSI crossings with an ADX filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451723_laguerre_rsi_cross_adx_filter_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "alpha": [0.2, 0.5],
    "adx_level": [20, 25],
}
DEFAULT_PARAMS = {"alpha": 0.2, "adx_level": 20.0, "buy_lvl": 20.0, "sell_lvl": 80.0,
                  "adx_len": 14, "adx_smooth": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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


def _laguerre_rsi(c, alpha):
    g = 1 - alpha
    v = c.to_numpy(dtype=float)
    out = np.zeros(len(v))
    p0 = p1 = p2 = p3 = 0.0
    for i in range(len(v)):
        l0 = (1 - g) * v[i] + g * p0
        l1 = -g * l0 + p0 + g * p1
        l2 = -g * l1 + p1 + g * p2
        l3 = -g * l2 + p2 + g * p3
        cu = (l0 - l1 if l0 > l1 else 0) + (l1 - l2 if l1 > l2 else 0) + (l2 - l3 if l2 > l3 else 0)
        cd = (l1 - l0 if l0 < l1 else 0) + (l2 - l1 if l1 < l2 else 0) + (l3 - l2 if l2 < l3 else 0)
        out[i] = 0.0 if cu + cd == 0 else cu / (cu + cd)
        p0, p1, p2, p3 = l0, l1, l2, l3
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h - h.shift(1), lo.shift(1) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    k = int(p["adx_len"])
    atr = _rma(tr, k)
    dip, dim = 100 * _rma(pdm, k) / atr, 100 * _rma(mdm, k) / atr
    s = dip + dim
    adx = 100 * _rma((dip - dim).abs() / s.where(s != 0, 1.0), int(p["adx_smooth"]))
    strong = adx > float(p["adx_level"])
    lr = 100 * _laguerre_rsi(c, float(p["alpha"]))
    b, sv = float(p["buy_lvl"]), float(p["sell_lvl"])
    le = (lr > b) & (lr.shift(1) <= b) & strong
    se = (lr < sv) & (lr.shift(1) >= sv) & strong
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
