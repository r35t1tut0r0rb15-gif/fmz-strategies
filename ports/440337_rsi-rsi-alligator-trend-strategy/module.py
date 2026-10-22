"""RSI alligator, 1-hour bars, long only (the default type): the RSI 13 crossing over the RSI 34 with the RSI 5 above the RSI 13 goes long; the mirror crossing closes; a 10 % stop and a 90 % target from
the entry.
Port of FMZ strategy #440337 "RSI鳄鱼趋势策略RSI-Alligator-Trend-Strategy" (RSI Alligator Strategy).

FMZ source id: 440337

Source
    https://www.fmz.com/strategy/440337 (PineScript v3, FMZ last modified 2024-01-29 14:40:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 185-251), RSI 5 / 13 / 34 (offsets 0); type Long Only; stop 10 %, target 90 %; date window 2018-07 to 2020-12 (window() returns true)
    LONG = crossover(teeth, lips) and jaws > teeth;  SHORT = crossunder(teeth, lips) and jaws < teeth;  Long Only: buy -> entry Long, sell -> close Long
    strategy.exit("Stop Loss/Profit", "Long", stop = avg price x (1 - 10 %), limit = avg price x (1 + 90 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The type input defaults to Long Only, which is ported; the other types are not. The date window is
      not applied (window() returns true). The bracket is fixed fractions of the entry: sl_stop 0.10,
      tp_stop 0.90. An entry while long is ignored (pyramiding 0), so trades start only from flat. Long
      only. Stop module: portfolio_kwargs {} (driver D4). The cash size, capital, commission and
      slippage settings are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, RSI crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash size, capital, commission and slippage settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440337_rsi_alligator_long_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.10, 0.03],
    "tp": [0.90, 0.10],
}
DEFAULT_PARAMS = {"sl": 0.10, "tp": 0.90, "jaw": 5, "teeth": 13, "lips": 34}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    jaws, teeth, lips = (_rsi(c, int(p[k])) for k in ("jaw", "teeth", "lips"))
    buy = ((teeth > lips) & (teeth.shift(1) <= lips.shift(1)) & (jaws > teeth)).to_numpy()
    sell = ((teeth < lips) & (teeth.shift(1) >= lips.shift(1)) & (jaws < teeth)).to_numpy()
    s_, t_ = float(p["sl"]), float(p["tp"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 1 and sell[i] and i >= entry_i:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
