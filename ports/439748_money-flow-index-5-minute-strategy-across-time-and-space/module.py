"""One-minute bars: an MFI 3 of 100 on the previous bar followed by an up bar with a body over half its range above the SMA 80 goes long; an MFI of 0 followed by such a down bar under the SMA goes short; only shorts carry a bracket (stop 3 % above the high of the day's 00:00 UTC bar, target 2.2 times that distance); reversing.
Port of FMZ strategy #439748 "Money Flow Index 5 Minute Strategy Across Time and Space" (Money Flow Index 5 min Strategy (tweakerID)).

FMZ source id: 439748

Source
    https://www.fmz.com/strategy/439748 (PineScript v4, FMZ last modified 2024-01-23 14:46:55).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 167-302), MFI 3, 100 / 0; body 0.5; SMA 80 filter; mirrored shorts; Strategy Stop (day-start bar +-3 %), R:R 2.2; direct reverse on; timed exit off
    BUY = MFI[1] == 100 and close > open and shortwicksbar and close > sma(close, 80) -> entry long;  SELL = MFI[1] == 0 and close < open and shortwicksbar and close < SMA -> entry short
    exit("TP & SL", "long", limit = TP, stop = LongStop);  exit("TP & SL", "short", limit = STP, stop = ShortStop)  (one id)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits share one id, so the second call (from_entry "short") replaces the first every bar:
      only shorts get the bracket, longs end only by the reversal (as #435894; weird case). ShortStop is
      the high of the day's 00:00 UTC bar x 1.03 (the last such bar) and the target the average price
      minus 2.2 times its distance; the level is re-sent every bar and moves at each new day, so the
      port fixes it at the signal bar as fractions of the fill (mark trailing_stop_pending); a stop the
      fill has already passed leaves no bracket. MFI as Pine's on the close; a window with neither
      rising nor falling flow has no value. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short-only bracket fixed at the signal bar.
    2 generic: PASS, MFI extremes followed by strong candles with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) in the MFI 3; exchange volume to be compared later (Austin, 2026-10-23).
Session open: day start = the 00:00 UTC bar (header exchange time) for the short stop.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439748_mfi3_extreme_strong_candle_sma80_short_daystop_1m_reversal"
FAMILY = "mfi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [80, 40],
    "body": [0.5, 0.7],
}
DEFAULT_PARAMS = {"mfi_len": 3, "ob": 100.0, "os": 0.0, "body": 0.5, "ma_len": 80, "perc_inc": 0.03, "rrr": 2.2}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _mfi(src, vol, n):
    """Pine ta.mfi: 100 when the falling flow is 0, 0 when the rising is 0, none when both are 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    out = out.where(upper != 0, 0.0).where(lower != 0, 100.0)
    return out.where(upper.notna() & lower.notna() & ~((upper == 0) & (lower == 0)))


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    mfi = _mfi(c, v, int(p["mfi_len"])).shift(1)
    strong = (c - o).abs() > (h - lo) * float(p["body"])
    above = c > c.rolling(int(p["ma_len"])).mean()
    below = c <= c.rolling(int(p["ma_len"])).mean()
    buy = (mfi == float(p["ob"])) & (c > o) & strong & above
    sell = (mfi == float(p["os"])) & (c < o) & strong & below
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h = bars_df["open"], bars_df["high"]
    ix = bars_df.index
    day_start = (ix.hour == 0) & (ix.minute == 0)
    short_stop = _fixnan(pd.Series(np.where(day_start, h.to_numpy(dtype=float), np.nan), index=ix)) * (1 + float(p["perc_inc"]))
    short_fill = se.shift(1, fill_value=False)          # only the 'short' entry keeps the shared exit
    sl_f = (short_stop.shift(1) / o - 1).where(short_fill)
    sl_f = sl_f.where(sl_f > 0)
    return {"sl_stop": sl_f, "tp_stop": float(p["rrr"]) * sl_f}


def portfolio_kwargs(**params):
    return {}
