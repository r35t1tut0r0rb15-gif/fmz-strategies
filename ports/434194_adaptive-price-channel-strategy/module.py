"""ADX-switched price-channel entries, 1-hour bars: with the ADX 20 under 25, a close above the 20-bar high minus 3.2 ATR
goes long, otherwise a close below the 20-bar low plus 3.2 ATR goes short; with the ADX at 25 or more only the side of the
stronger DI may enter. The bar-count exit never fires (see below), so positions change only by reversal.
Port of FMZ strategy #434194 "Adaptive Price Channel Strategy" (Adaptive Price Channel Strategy).

FMZ source id: 434194

Source
    https://www.fmz.com/strategy/434194 (PineScript v5, FMZ last modified 2023-12-04 16:33:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 137-184), length 20, exit after 10 bars, ATR multiplier 3.2
    adx < 25: close > hh - 3.2 atr -> entry long, else close < ll + 3.2 atr -> entry short;  adx >= 25 and +DI > -DI: the long test only;  +DI < -DI: the short test only
    barSinceEntry: set to 0 on an entry;  na -> na + 1;  >= 10 -> close both, na  (it is never incremented from 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the bar counter is set to 0 by an entry and never counts up (only an undefined value
      is "incremented"), so the 10-bar exit never fires. The entries are levels (ignored when already
      in that position). Entries start once 20 bars exist.
    * +DI / -DI use rma of the directional moves over ta.atr(20); ADX = rma(dx, 20).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel distances in ATR and DI / ADX levels.
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

NAME = "fmz_434194_adx_switched_price_channel"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "atr_mult": [3.2, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "atr_mult": 3.2, "adx_level": 25.0}


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
    n = int(p["length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    um, dm = h - h.shift(1), lo.shift(1) - lo
    pdm = pd.Series(np.where((um > dm) & (um > 0), um, 0.0), index=c.index).where(um.shift(1).notna())
    mdm = pd.Series(np.where((dm > um) & (dm > 0), dm, 0.0), index=c.index).where(dm.shift(1).notna())
    pdi = pdm.ewm(alpha=1 / n, adjust=False).mean() / atr * 100
    mdi = mdm.ewm(alpha=1 / n, adjust=False).mean() / atr * 100
    dx = (pdi - mdi).abs() / (pdi + mdi) * 100
    adx = dx.ewm(alpha=1 / n, adjust=False).mean()
    k = float(p["atr_mult"])
    lt = (c > hh - k * atr).to_numpy()
    st = (c < ll + k * atr).to_numpy()
    lvl = float(p["adx_level"])
    side = adx < lvl
    bull = (adx >= lvl) & (pdi > mdi)
    bear = (adx >= lvl) & (pdi < mdi)
    ready = c.shift(n).notna().to_numpy()
    sv, bu, be = side.to_numpy(), bull.to_numpy(), bear.to_numpy()
    le = ready & ((sv & lt) | (bu & lt))
    se = ready & ((sv & ~lt & st) | (be & st))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
