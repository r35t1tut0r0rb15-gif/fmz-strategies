"""Closes beyond the previous day's high (low) with EMA 9 on the matching side of EMA 21, with a tick stop as an ATR
multiple and a 2 R target from the entry, 1-hour bars: a close above the previous broker day's high with EMA 9 above
EMA 21 goes long; a close below the previous day's low with EMA 9 below EMA 21 goes short.
Port of FMZ strategy #483092 "基于日内价格区间突破的动量交易策略结合EMAs指标优化-Price-Range-Breakout-Momentum-Trading-Strategy-with-EMAs-Optimization" (GER40 Momentum Breakout Scalping).

FMZ source id: 483092

Source
    https://www.fmz.com/strategy/483092 (PineScript v5, FMZ last modified 2025-02-21 13:20:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-148), SL 30 ticks, RR 2, time filter off
    prevHigh / prevLow = request.security("D", high[1] / low[1]); EMA 9 / 21
    long = close > prevHigh and ema9 > ema21 -> entry + exit(stop = avg_price - 30 ticks, limit = avg_price + 60 ticks)
    short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The previous day is the last completed broker day (17:00 America/New_York), built from the port's own bars (house
      request.security rule, as #430771); the author's chart day was the UTC day.
    * The exit is issued on signal bars from strategy.position_avg_price, na while flat: a trade opened from flat gets
      its bracket only from a later same-side signal. The port applies it from the fill (the evident intent), as
      #489289. Decision owed: keep this, or port the literal behaviour. Re-issues use the same entry price, so the
      levels do not move.
    * Tick distances -> ATR(14) multiples (criterion 2), judged on the author's market (Binance SOL_USDT, 1h, mintick
      0.01, ATR about 1.8 USD in early 2025): 30 ticks = 0.30 USD = 0.17 ATR; the target rr x that. GER40 in the title
      is a label. sl_stop = sl_k x ATR / close of the signal bar, shifted one bar inside stops(), re-based on the fill.
    * The time filter is off by default and, as written, inert (the `inSession` inside the if is a new local
      variable).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill (decision owed).
    2 generic: PASS, previous-day extremes, EMAs and tick distances as ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the previous day's high / low; no venue-open
    rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483092_prev_day_breakout_ema_tick_bracket"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_k": [0.17, 0.5],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "sl_k": 0.17, "rr": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lab = broker_day(bars_df.index)
    day = pd.DataFrame({"h": h.to_numpy(), "l": lo.to_numpy()}, index=lab)
    d = day.groupby(level=0).agg({"h": "max", "l": "min"})
    prev = d.shift(1).reindex(lab)                       # the last completed broker day
    ph = pd.Series(prev["h"].to_numpy(), index=c.index)
    pl = pd.Series(prev["l"].to_numpy(), index=c.index)
    ef, es = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    long_e = ((c > ph) & (ef > es)).astype(bool)
    short_e = ((c < pl) & (ef < es)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_k"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
