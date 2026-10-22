"""A composite of 63 / 126 / 189 / 252-bar momentum turning positive while the 252-bar annualised return volatility is at most 0.5, hourly bars, long only: the turn goes long with a 5 % stop and a 15 % target from the fill; the composite turning negative (volatility still low) closes.
Port of FMZ strategy #483505 "Multi Period Momentum Driven Adaptive Volatility Filtered Strategy" (GOATED Long-Only).

FMZ source id: 483505

Source
    https://www.fmz.com/strategy/483505 (PineScript v5, FMZ last modified 2025-02-24 09:38:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-191), momentum periods 63 / 126 / 189 / 252; volatility threshold 0.5 (stdev of returns over 252 x sqrt 252); momentum threshold 0; stop 5 %; target 15 %; 100 % of equity, capital 1000
    composite = mean of the available close / close[n] - 1;  valid = composite > 0;  vol_ok = annualised vol <= 0.5
    vol_ok and valid and not valid[1] -> entry Long;  long -> exit(stop = avg x 0.95, limit = avg x 1.15);  vol_ok and not valid and valid[1] -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The periods are counted in the chart's bars (hourly here), as written, and the annualisation uses
      sqrt(252) on hourly returns, as written. The bracket is sent from the fill bar's close around the
      average price; it is ported as fixed fractions of the fill, active from the fill bar (as #440797).
      Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). The 100 % of
      equity size and the capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, composite momentum turns with a volatility ceiling.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483505_composite_momentum_turn_vol_ceiling_5_15pct_bracket_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss": [0.05, 0.03],
    "take_profit": [0.15, 0.1],
}
DEFAULT_PARAMS = {"stop_loss": 0.05, "take_profit": 0.15, "vol_threshold": 0.5, "mom_threshold": 0.0,
                  "periods": "63,126,189,252", "vol_window": 252}


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
    c = bars_df["close"]
    moms = [c / c.shift(int(k)) - 1 for k in str(p["periods"]).split(",")]
    tot = sum(m.fillna(0.0) for m in moms)
    cnt = sum(m.notna().astype(float) for m in moms)
    comp = (tot / cnt).where(cnt > 0)
    w = int(p["vol_window"])
    vol = (c.diff() / c.shift(1)).rolling(w).std() * np.sqrt(w)
    vol_ok = vol.notna() & (vol <= float(p["vol_threshold"]))
    valid = comp.notna() & (comp > float(p["mom_threshold"]))
    prev = valid.shift(1, fill_value=False)
    le = vol_ok & valid & ~prev
    lx = vol_ok & ~valid & prev
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss"]), index=idx).shift(1)
    tp = pd.Series(float(p["take_profit"]), index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
