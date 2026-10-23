"""AlphaTrend (MFI 14 of hlc3 at 50 choosing a ratcheting low - 1 ATR or high + 1 ATR line, ATR = SMA 14 of the true range) crossing over its value 2 bars back goes long, crossing under it goes short, hourly bars, with a 10 % trailing stop from the best close; reversing.
Port of FMZ strategy #433423 "Alpha趋势跟踪止损策略Alpha-Trend-Strategy-with-Trailing-Stop-Loss" (AlphaTrend Strategy (KivancOzbilgic)).

FMZ source id: 433423

Source
    https://www.fmz.com/strategy/433423 (PineScript v5, FMZ last modified 2023-11-27 15:25:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 142-223), coeff 1; period 14; MFI (volume data on); trailing stop 10 % of the close, on
    AlphaTrend := mfi(hlc3, 14) >= 50 ? (low - ATR < nz(AT[1]) ? nz(AT[1]) : low - ATR) : (high + ATR > nz(AT[1]) ? nz(AT[1]) : high + ATR)
    crossover(AT, AT[2]) -> entry Long;  crossunder(AT, AT[2]) -> entry Short;  longStopPrice := max(close x 0.9, longStopPrice[1]) while long -> exit(stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.mfi(hlc3, 14) as Pine defines it (100 when the falling flow is 0, 0 when the rising is 0); ta.tr
      is na on the first bar. The trail is the script's ratchet of 90 % of each hourly CLOSE while in the
      position (110 % for shorts), sent from the bar after the fill: ported as the house percent trail
      {"pct": 0.10, "anchor": "close"}, which ratchets on minute closes (stated approximation, mark
      trailing_stop; the hourly-close ratchet itself is not expressible: trailing_stop_pending).
      REVERSAL INTENDED. margin_long / margin_short 100 are sizing. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: PASS, AlphaTrend line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): margin_long 100, margin_short 100, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in ta.mfi(hlc3, 14), which picks the AlphaTrend line; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_433423_alphatrend_mfi14_atr1_cross_pct_trail_reversal"
FAMILY = "alphatrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "coeff": [1.0, 2.0],
    "trail_pct": [0.10, 0.05],
}
DEFAULT_PARAMS = {"coeff": 1.0, "ap": 14, "trail_pct": 0.10}


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
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    ap = int(p["ap"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = tr.rolling(ap).mean()
    up_t = (lo - atr * float(p["coeff"])).to_numpy(dtype=float)
    dn_t = (h + atr * float(p["coeff"])).to_numpy(dtype=float)
    bull = (_mfi((h + lo + c) / 3, v, ap) >= 50).to_numpy()
    m = len(up_t)
    at = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        p0 = 0.0 if np.isnan(prev) else prev
        if bull[i]:
            at[i] = p0 if up_t[i] < p0 else up_t[i]
        else:
            at[i] = p0 if dn_t[i] > p0 else dn_t[i]
        prev = at[i]
    a = pd.Series(at, index=c.index)
    a2 = a.shift(2)
    buy = (a > a2) & (a.shift(1) <= a2.shift(1))
    sell = (a < a2) & (a.shift(1) >= a2.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.fillna(False).astype(bool), false, sell.fillna(False).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
