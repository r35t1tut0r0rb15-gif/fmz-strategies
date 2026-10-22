"""Five-layer volatility bands around an SMA 12, 2-hour bars: a close under any armed lower layer goes long (the layer then waits until a low over the basis re-arms it), a close over any armed upper layer goes short (re-armed by a high under the basis); reversing.
Port of FMZ strategy #458264 "Multi Layer Volatility Band Trading Strategy" (Spider Strategy).

FMZ source id: 458264

Source
    https://www.fmz.com/strategy/458264 (PineScript v5, FMZ last modified 2024-07-31 14:08:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-360), collective value 12 (stdev, basis and ATR lengths all 12); dynamic multiplier = SMA 12 of the true range x 0.72; bands basis +- 12 x mult x (1, 0.236, 0.382, 0.5, 0.618); 1 share; basis exit off
    each lower layer k: not armed-used and close < lower_k -> entry long, used;  used and low > basis -> re-armed
    each upper layer k: not used and close > upper_k -> entry short, used;  used and high < basis -> re-armed

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default switches the "stdev" input is the plain number 12 (the collective value), so the
      band half-width is 12 x 0.72 x SMA 12 of the true range times each layer's factor. Every layer
      enters with the same id, so with the default pyramiding of 1 a further layer's entry while held
      does nothing; the layer flags still follow as written. The basis exit is off by default, so
      positions end at the opposite entry. The 1-share quantity is not ported. REVERSAL INTENDED. FREQ =
      "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, layered volatility-band fades.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1-share quantity stored, not ported.
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

NAME = "fmz_458264_layered_tr_band_fades_rearm_at_basis_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "col_int": [12, 30],
    "atr_bias": [0.72, 1.0],
}
DEFAULT_PARAMS = {"col_int": 12, "atr_bias": 0.72}
FIBS = (1.0, 0.236, 0.382, 0.5, 0.618)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["col_int"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # ta.tr(true)
    mult = tr.rolling(n).mean() * float(p["atr_bias"])
    basis = c.rolling(n).mean()
    half = n * mult
    lows = [(basis - half * f).to_numpy() for f in FIBS]
    ups = [(basis + half * f).to_numpy() for f in FIBS]
    bv, hv, lv, cv = basis.to_numpy(), h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    l_used, u_used = [False] * 5, [False] * 5
    for i in range(m):
        for k in range(5):
            if not l_used[k]:
                if cv[i] < lows[k][i]:
                    le[i], l_used[k] = True, True
            elif lv[i] > bv[i]:
                l_used[k] = False
        for k in range(5):
            if not u_used[k]:
                if cv[i] > ups[k][i]:
                    se[i], u_used[k] = True, True
            elif hv[i] < bv[i]:
                u_used[k] = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
