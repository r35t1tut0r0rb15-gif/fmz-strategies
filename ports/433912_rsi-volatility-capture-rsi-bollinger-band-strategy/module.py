"""A ratcheting Bollinger line with RSI confirmation, 15-minute bars: a line follows the price (rising with the lower band
of the lows while price is above it, falling with the upper band of the highs while below); hlc3 crossing above it with
the SMA 5 of RSI 10 above 55 goes long (the line resets to the lower band), crossing below with that average under 50
goes short (the line resets to the upper band); a close crossing back through the line closes the position.
Port of FMZ strategy #433912 "动态波幅捕捉RSI-布林带策略Volatility-Capture-RSI-Bollinger-Band-Strategy" (Volatility Capture RSI-Bollinger - Strategy [presentTrading]).

FMZ source id: 433912

Source
    https://www.fmz.com/strategy/433912 (PineScript v5, FMZ last modified 2023-12-01 14:17:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-201), source hlc3, length 50, multiplier 2.7183 (on sma / stdev of highs and lows), RSI 10, SMA 5, levels 55 / 50; both directions
    upper = sma(high, 50) + 2.7183 stdev(high, 50);  lower = sma(low, 50) - 2.7183 stdev(low, 50)
    pb := close > pb ? max(pb, lower) : close < pb ? min(pb, upper) : 0  (0 until both bands exist)
    crossover(hlc3, pb) and sma(rsi, 5) > 55 -> pb := lower, entry long;  crossunder and < 50 -> pb := upper, entry short
    long and crossunder(close, pb) -> close;  short and crossover(close, pb) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry crosses are evaluated before the line is updated, so they compare hlc3 now and one bar
      ago with the line as it stood at the end of the previous bar; the exit crosses use the updated
      line, as in the source's statement order. Pine's stdev is the population stdev; RSI is Wilder's, on hlc3.
    * An exit on the bar of an opposite entry is left to the entry (strategy.entry reverses):
      REVERSAL INTENDED. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a band-following line and RSI levels.
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

NAME = "fmz_433912_ratchet_band_rsi"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 25],
    "mult": [2.7183, 2.0],
}
DEFAULT_PARAMS = {"length": 50, "mult": 2.7183, "rsi_len": 10, "sma_len": 5, "bought": 55.0, "sold": 50.0}


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
    src = (h + lo + c) / 3
    n, k = int(p["length"]), float(p["mult"])
    ub = (h.rolling(n).mean() + h.rolling(n).std(ddof=0) * k).to_numpy()
    lb = (lo.rolling(n).mean() - lo.rolling(n).std(ddof=0) * k).to_numpy()
    ch = src.diff()
    rn = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / rn, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / rn, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    rs = r.rolling(int(p["sma_len"])).mean().to_numpy()
    sv, cv = src.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pb_end = np.full(m, np.nan)
    pos = 0
    for i in range(m):
        prev_end = pb_end[i - 1] if i > 0 else np.nan
        # entry crosses: before its update the line still holds the previous bar's value, which is
        # also its [1] value, so both sides of the cross compare with that value
        x_up = i > 0 and sv[i] > prev_end and sv[i - 1] <= prev_end
        x_dn = i > 0 and sv[i] < prev_end and sv[i - 1] >= prev_end
        if np.isnan(lb[i]) or np.isnan(ub[i]):
            pb = 0.0
        elif cv[i] > (prev_end if not np.isnan(prev_end) else 0.0):
            pb = max(prev_end if not np.isnan(prev_end) else 0.0, lb[i])
        elif cv[i] < (prev_end if not np.isnan(prev_end) else 0.0):
            pb = min(prev_end, ub[i])
        else:
            pb = 0.0
        start = pos
        entered = False
        if x_up and rs[i] > p["bought"]:
            pb, pos, entered = lb[i], 1, True
        if x_dn and rs[i] < p["sold"]:
            pb, pos, entered = ub[i], -1, True
        pb_end[i] = pb
        if not entered and i > 0:
            if start == 1 and cv[i] < pb and cv[i - 1] >= prev_end:
                pos = 0
            elif start == -1 and cv[i] > pb and cv[i - 1] <= prev_end:
                pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
