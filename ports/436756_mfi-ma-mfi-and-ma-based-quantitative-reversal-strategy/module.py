"""One-minute bars: after a bar whose MFI 3 of the close was exactly 100, a green bar with a body over half its range above the SMA 80 goes long; after an MFI of exactly 0, a red such bar below the SMA goes short; reversing (the script's target / stop never exist on a fresh entry).
Port of FMZ strategy #436756 "基于MFI和MA的量化反转策略MFI-and-MA-Based-Quantitative-Reversal-Strategy" ([VJ]Thor for MFI (vikris)).

FMZ source id: 436756

Source
    https://www.fmz.com/strategy/436756 (PineScript v4, FMZ last modified 2023-12-27 14:42:16).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 157-252), MFI 3, overbought 100, oversold 0; body 0.5 of the range; SMA 80 filter on; TP 1 %, SL 0.5 % (see interp); session 0915-1455 (not used)
    BUY = mfi(close, 3)[1] == 100 and close > open and body > 0.5 range and close > sma(close, 80) -> entry Buy, exit(stop = avg x 0.995, limit = avg x 1.01)
    SELL = mfi[1] == 0 and close < open and body > 0.5 range and close < sma -> entry Sell, exit(stop = avg x 1.005, limit = avg x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on the signal bar from strategy.position_avg_price, which is na while flat, so a
      fresh entry has no exit order; it only gets one when a signal repeats while in a position (and a
      reversal takes the levels from the old position's average). That path-dependent bracket is not
      ported (weird case, as #434555): positions end only at the opposite entry. intradaySession is true,
      so the square-off never fires and the session input is unused. ta.mfi(close, 3) as Pine defines it.
      REVERSAL INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MFI extreme follow-through bars with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in ta.mfi(close, 3); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (intradaySession is always true).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436756_mfi3_extreme_body_bar_sma80_1m_reversal"
FAMILY = "mfi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mfi_len": [3, 5],
    "ma_len": [80, 200],
}
DEFAULT_PARAMS = {"mfi_len": 3, "ob": 100.0, "os": 0.0, "body": 0.5, "ma_len": 80}


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
    """Pine ta.mfi: money-flow ratio over n bars; 100 when the falling flow is 0, 0 when the rising is 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    return out.where(upper != 0, 0.0).where(lower != 0, 100.0).where(upper.notna() & lower.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    mf1 = _mfi(c, v, int(p["mfi_len"])).shift(1)
    body = (c - o).abs() > (h - lo) * float(p["body"])
    sma = c.rolling(int(p["ma_len"])).mean()
    buy = (mf1 == float(p["ob"])) & (c > o) & body & (c > sma)
    sell = (mf1 == float(p["os"])) & (c < o) & body & (c <= sma)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy & ~sell, false, sell & ~buy, false.copy()


def portfolio_kwargs(**params):
    return {}
