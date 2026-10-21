"""ATR "Renko" box steps, 1-hour bars: a close one or two box heights above the previous box top moves the box up (by 1 or 2 ATR 60) and goes long; the mirror moves it down and goes short; reversing.
Port of FMZ strategy #437503 "基于ATR通道的破口踏入趋势策略ATR-Channel-Breakout-Trend-following-Strategy" (RENKO-Trend str.).

FMZ source id: 437503

Source
    https://www.fmz.com/strategy/437503 (PineScript v5, FMZ last modified 2024-01-03 11:53:52).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 107-180), time frame 60 (the chart's own), ATR 60
    RENKOUP / RENKODN seeded at (high + low) / 2 +- ATR / 2;  H = previous box height;  close >= RENKOUP[1] + 2H -> box up 2 ATR, UP;  close >= RENKOUP[1] + H -> box up 1 ATR, UP;  mirror for DN
    UP -> entry Long;  DN -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The time frame input equals the 1-hour chart, so the security() values are the chart's own. The box
      follows the script: the step tests the previous box, the moves use the current ATR, only the first
      true test of the four applies (as #436765, two steps here). REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR box steps.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437503_atr_renko_box_steps"
FAMILY = "breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_length": [60, 30],
}
DEFAULT_PARAMS = {"atr_length": 60}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a4 = _rma(tr, int(p["atr_length"])).to_numpy()
    hh, ll, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    upv, dnv = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ru_p = rd_p = np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if np.isnan(ru_p):
                ru = (hh[i] + ll[i]) / 2 + a4[i] / 2
                rd = (hh[i] + ll[i]) / 2 - a4[i] / 2
            else:
                ru, rd = ru_p, rd_p
            hb = ru - rd if (np.isnan(ru_p) or np.isnan(rd_p)) else ru_p - rd_p
            for k in (2, 1):
                if cv[i] >= ru_p + hb * k:
                    upv[i] = True
                    ru, rd = ru_p + a4[i] * k, ru_p + a4[i] * (k - 1)
                    break
            else:
                for k in (2, 1):
                    if cv[i] <= rd_p - hb * k:
                        dnv[i] = True
                        rd, ru = rd_p - a4[i] * k, rd_p - a4[i] * (k - 1)
                        break
            ru_p, rd_p = ru, rd
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(upv, index=ix), false, pd.Series(dnv, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
