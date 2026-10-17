"""Smeared variability channel index crosses, 1-hour bars: the SMA 34 of (EMA 5 - EMA 13) / ATR 96 crossing above its SMA 13
trigger goes long, crossing below goes short; each trade has a 300-tick stop and a 1-tick trail that starts after 150
ticks of profit (house stop and trail).
Port of FMZ strategy #432234 "Trend Following Energy Indicator Trading Strategy" (Smeared VCI Backtest).

FMZ source id: 432234

Source
    https://www.fmz.com/strategy/432234 (PineScript v3, FMZ last modified 2023-11-15 17:36:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 194-240), EMA 5 / 13, ATR 96, smear 34, trigger 13, SL 300 ticks, trail 150 points / offset 1
    vci = (ema5 - ema13) / atr(96); svci = sma(vci, 34); t = sma(svci, 13)
    crossover(svci, t) -> entry long;  crossover(t, svci) -> entry short
    exit("Exit", loss = 300, trail_points = 150, trail_offset = 1) for any entry; exit("Exit", when = ...) with no levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: on hourly BTC (0.1 tick, ATR about 200 USD) the 300-tick stop is about 0.15 ATR, the
      trail activates after 150 ticks (15 USD, about 0.0004 of the price) and trails 1 tick behind the
      best price (about 0.0005 ATR). Ported: sl_atr x Wilder ATR(14) of the signal bar (shifted,
      re-based) and the house trail {"type": "volatility", "atr_n": 14, "k": 0.0005, "anchor":
      "high_low", "activate_after": 0.0004} (stated approximation of the tick offsets, as #429564;
      mark trailing_stop).
    * The exit calls with only `when` place no order (as #429564). The date window (2019 to 2030) is
      the author's backtest range: dropped. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick distances -> ATR multiples / a fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the slippage stored; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_432234_smeared_vci_cross"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "smear": [34, 17],
    "sl_atr": [0.15, 1.0],
}
DEFAULT_PARAMS = {"ep1": 5, "ep2": 13, "atr_p": 96, "smear": 34, "trigger": 13, "atr_len": 14, "sl_atr": 0.15,
                  "trail_k": 0.0005, "trail_activate": 0.0004}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    vci = (c.ewm(span=int(p["ep1"]), adjust=False).mean() - c.ewm(span=int(p["ep2"]), adjust=False).mean()) \
        / _atr(bars_df, int(p["atr_p"]))
    sv = vci.rolling(int(p["smear"])).mean()
    t = sv.rolling(int(p["trigger"])).mean()
    le = ((sv > t) & (sv.shift(1) <= t.shift(1))).astype(bool)
    se = ((t > sv) & (t.shift(1) <= sv.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
