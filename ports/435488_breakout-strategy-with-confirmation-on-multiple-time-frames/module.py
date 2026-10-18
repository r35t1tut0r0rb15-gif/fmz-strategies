"""Daily-open breakout with candlestick confirmation, 1-hour bars, always in the market after the first trade: the last close of a
370-minute bar crossing over the open of the daily bar goes long (under it, short); before the first trade, a close over the daily
open with a bullish pattern (or under it with a bearish one) also opens a position.
Port of FMZ strategy #435488 "Breakout Strategy with Confirmation on Multiple Time Frames" (breakout).

FMZ source id: 435488

Source
    https://www.fmz.com/strategy/435488 (PineScript v2, FMZ last modified 2023-12-15 12:16:55).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 158-381), tim 1440 (daily open), sim 370 (370-minute close); pin bar 66 %; dark cloud, piercing line, engulfing and harami patterns on; fractal and CM patterns off
    out1 = security(tickerid, "1440", open);  out2 = security(tickerid, "370", close)
    bullcnd = pBarUp or pln or blh or ble;  bearcnd = pBarDn or dcc or beh or bee   (the fractal term needs "Use Fractal S/R Cross Patterns", off)
    crossover(out2, out1) or (close > out1 and bullcnd and flat) -> entry long;  crossunder(out2, out1) or (close < out1 and bearcnd and flat) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security without lookahead gives the last completed higher bar. The daily bar is the
      broker day (17:00 America/New_York); the 370-minute bars restart at each broker-day open (the
      last one of the day is shorter). precompute builds both on the loader's minutes: a value is
      used from the first 1-hour bar that ends at or after the higher bar's end, so no minute after
      the bar's end is read.
    * The orders never close: after the first entry the position is never flat, so the pattern
      clauses (which need a flat position) act only before the first trade, and every later trade is
      a reversal on a cross: REVERSAL INTENDED. When both sides fire on one bar, the short (sent
      last) stands. The trend, MACD and colour options only colour bars. The patterns use the
      ranges as written (a zero range gives no signal).
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher-timeframe values from completed bars.
    2 generic: REVIEW, patterns act only before the first trade; reversals on crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily open and the 370-minute blocks (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435488_daily_open_370_cross_patterns"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pct_p": [66, 75],
    "sim": [370, 240],
}
DEFAULT_PARAMS = {"pct_p": 66, "sim": 370}

_EPOCH = pd.Timestamp("1970-01-01", tz="UTC")


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _mn(ix):
    """Whole minutes since the epoch of a tz-aware index (independent of the index's time unit)."""
    return np.asarray((ix - _EPOCH) // pd.Timedelta(minutes=1), dtype=np.int64)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    ohlc = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.resample(FREQ, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    lab = broker_day(ohlc.index)
    ds = _mn((lab - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York").tz_convert("UTC"))
    de = _mn((lab + pd.Timedelta(hours=17)).tz_localize("America/New_York").tz_convert("UTC"))
    t = _mn(ohlc.index)
    sim = int(p["sim"])
    blk = (t - ds) // sim
    bend = np.minimum(ds + (blk + 1) * sim, de)
    frame = pd.DataFrame({"de": de, "blk": blk, "bend": bend, "open": ohlc["open"].to_numpy(),
                          "close": ohlc["close"].to_numpy()})
    blocks = frame.groupby(["de", "blk"], sort=True).agg(end=("bend", "first"), close=("close", "last"))
    days = frame.groupby("de", sort=True).agg(open=("open", "first"))
    bar_end = _mn(bars.index) + 60
    k2 = np.searchsorted(blocks["end"].to_numpy(), bar_end, side="right") - 1
    k1 = np.searchsorted(days.index.to_numpy(), bar_end, side="right") - 1
    bars["htf_close"] = np.where(k2 >= 0, blocks["close"].to_numpy()[np.maximum(k2, 0)], np.nan)
    bars["htf_open"] = np.where(k1 >= 0, days["open"].to_numpy()[np.maximum(k1, 0)], np.nan)
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    out1, out2 = bars_df["htf_open"], bars_df["htf_close"]
    rng = h - lo
    pc = float(p["pct_p"]) * 0.01
    o1, c1, h1, l1, r1 = o.shift(1), c.shift(1), h.shift(1), lo.shift(1), rng.shift(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        body1 = (c1 - o1).abs() / r1
        body0 = (c - o).abs() / rng
        pbar_dn = (o < h - rng * pc) & (c < h - rng * pc)
        pbar_up = (o > lo + rng * pc) & (c > lo + rng * pc)
        dcc = ((c1 > o1) & (body1 >= 0.7) & (c < o) & (body0 >= 0.7) & (o >= c1) & (c > o1)
               & (c < (o1 + c1) / 2))
        pln = ((c1 < o1) & (body1 >= 0.7) & (c > o) & (body0 >= 0.7) & (o <= c1) & (c < o1)
               & (c > (o1 + c1) / 2))
        inside = (h < h1) & (lo > l1)
        beh = (c1 > o1) & (o > c) & (o <= c1) & (lo >= o1) & ((o - c) < (c1 - o1)) & inside
        blh = (o1 > c1) & (c > o) & (c <= o1) & (h <= o1) & ((c - o) < (o1 - c1)) & inside
        bee = (c1 > o1) & (c < o) & (c <= l1) & (o >= c1)
        ble = (c1 < o1) & (c > o) & (c >= h1) & (o <= c1)
    bull = (pbar_up | pln | blh | ble).fillna(False).to_numpy()
    bear = (pbar_dn | dcc | beh | bee).fillna(False).to_numpy()
    lc = ((out2 > out1) & (out2.shift(1) <= out1.shift(1))).fillna(False).to_numpy()
    sc = ((out2 < out1) & (out2.shift(1) >= out1.shift(1))).fillna(False).to_numpy()
    up_ok = ((c > out1)).fillna(False).to_numpy()
    dn_ok = ((c < out1)).fillna(False).to_numpy()
    m = len(lc)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    started = False
    for i in range(m):
        go_l = lc[i] or (up_ok[i] and bull[i] and not started)
        go_s = sc[i] or (dn_ok[i] and bear[i] and not started)
        if go_s:
            se[i] = True
        elif go_l:
            le[i] = True
        if go_l or go_s:
            started = True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
