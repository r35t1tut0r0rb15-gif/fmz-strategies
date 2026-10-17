"""WMA 20 pierce fades with a tick trail, 1-hour bars: inside the 16:00-05:00 session, a bar whose low dips under the WMA 20
goes long and a bar whose high pokes above it goes short (a bar doing both ends short); each trade has a 5-tick target
and a 10-tick trailing stop from the start, which become ATR multiples.
Port of FMZ strategy #433548 "Weighted Moving Average Breakout Reversal Strategy" (WMA Breakout).

FMZ source id: 433548

Source
    https://www.fmz.com/strategy/433548 (PineScript v3, FMZ last modified 2023-11-28 14:11:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 119-162), WMA 20; price drop / climb 0.003; trailing on: trail_points 0, offset 10 ticks, profit 5 ticks; session 1600-0500 ("Est time")
    z = low + 0.003 < wma ? wma - low : na -> entry long (in session);  a = high - 0.003 > wma ? high - wma : na -> entry short
    exit(profit = 5, trail_points = 0, trail_offset = 10) on each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 0.003 price-unit margins are negligible and dropped (criterion 2). A bar both under and above
      the WMA issues the long then the short entry and ends short.
    * Criterion 2 and C1: the bracket is in ticks. The 10-tick trail from the entry (activation 0) is
      ported natively as a house volatility trail, {"type": "volatility", "atr_n": 14, "k": trail_k,
      "anchor": "high_low"} (mark trailing_stop), and the 5-tick target as tp_stop = trail_k / 2 x ATR 14
      / close of the signal bar (shifted one bar, re-based on the fill), keeping the source's 5 : 10.
      Stated approximation: a fixed tick distance becomes an ATR distance that moves with the ATR. On
      the header's BTC_USDT 10 ticks are 1 USD (about 0.004 ATR); the script's futures reading (ES,
      tick 0.25: 2.5 points, about 0.25 ATR of hourly ES) is used.
    * Clock (C6): Pine's time(period, session) uses the exchange time zone (UTC on the header's
      BTC_USDT); the input says "Est time", so the grid declares America/New_York and UTC (DST by the
      zone). A bar is in the session when it opens inside 16:00-05:00.
    * REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house trail (approximation stated).
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the per-contract commission and quantity 1 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 16:00-05:00 entries, in America/New_York (the input's "Est") or UTC (header), DST by the zone; no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_433548_wma_pierce_fade_trail"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tz": ["America/New_York", "UTC"],
    "trail_k": [0.25, 1.0],
}
DEFAULT_PARAMS = {"tz": "America/New_York", "trail_k": 0.25, "wma_len": 20, "atr_len": 14, "sess_from": 960,
                  "sess_to": 300}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ (w / w.sum())
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    wm = _wma(c, int(p["wma_len"]))
    loc = bars_df.index.tz_convert(str(p["tz"]))
    mins = np.asarray(loc.hour * 60 + loc.minute)
    sess = (mins >= int(p["sess_from"])) | (mins < int(p["sess_to"]))
    dip = (lo < wm).to_numpy() & sess
    poke = (h > wm).to_numpy() & sess
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return dip & ~poke, poke, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    k = float(p["trail_k"])
    return {"tp_stop": (af * k / 2).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": k, "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
