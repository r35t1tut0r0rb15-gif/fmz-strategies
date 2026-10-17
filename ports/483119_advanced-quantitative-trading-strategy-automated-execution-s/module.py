"""Non-doji outside-up (inside-down) bars entered from flat between 01:00 and 19:00 London time, with a dollar stop /
target as ATR multiples and no new trade for the rest of the London day after a target is reached, 1-hour bars: a
green non-doji bar with a higher high and no lower low (first such bar in a row) goes long; the mirror goes short.
Port of FMZ strategy #483119 "高级量化交易策略基于日内动量与风险管理的自动化执行系统-Advanced-Quantitative-Trading-Strategy-Automated-Execution-System-Based-on-Intraday-Momentum-and-Risk-Management" (Trading Strategy for XAUUSD (Gold) - Automated Execution Plan).

FMZ source id: 483119

Source
    https://www.fmz.com/strategy/483119 (PineScript v6, FMZ last modified 2025-02-27 16:57:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-206), SL 5 $, TP 15 $
    doji = upper + lower shadow > body; buyRaw = high > high[1] and low >= low[1] and close > open and not doji
    buy = buyRaw and not buyRaw[1] (sell mirrored); from flat, London hour != 0 and < 19, no target hit today
    exit(stop = avg_price -+ 5 $, limit = avg_price +- 15 $) while held
    a trade closed on a bar whose high (low) reached its target blocks entries for the rest of the London day

Interpretation choices (Pine rules in SURVEY_README.md)
    * Dollar distances -> ATR(14) multiples (criterion 2), judged on the author's backtest market (Binance ETH_USDT,
      1h, ATR about 30 $): 5 $ = 0.17 ATR, 15 $ = 0.5 ATR. The title's market (XAUUSD, 1h ATR about 6 $) gives 0.8 /
      2.5 ATR: both readings are in the GRID. The fractions come from the signal bar (shifted one bar inside stops())
      and are re-based on the fill (house rule).
    * Entries only from flat: simulate() mirrors the house bracket on bars from the fill bar (as #430254 _run); an
      entry is allowed on the bar a stop or target is hit unless that bar's high (low) reached the target, which
      blocks the rest of the London day, as written. Opposite entries cannot occur.
    * Clock rule (check 9 / C6): hour(time, "Europe/London") of the bar's open: entries when it is not 0 and below 19,
      i.e. 01:00-18:59 Europe/London, DST by the zone; the day for the target lock-out is the Europe/London date.
    * lotSize (equity / initial capital) is sizing: not ported. Stop module: portfolio_kwargs {} (D4). FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill.
    2 generic: PASS, candle shapes and dollar distances as ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-scaled qty is quoted in original_sizing.txt and not ported; the bracket via stops().
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (an entry window 01:00-18:59 Europe/London by bar open time and a London-day lock-out, declared
    above).
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483119_outside_bar_london_window_daily_tp_lock"
FAMILY = "price_action"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_k": [0.17, 0.8],
    "tp_k": [0.5, 2.5],
}
DEFAULT_PARAMS = {"session_tz": "Europe/London", "atr_len": 14, "sl_k": 0.17, "tp_k": 0.5}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    doji = (h - np.maximum(o, c)) + (np.minimum(o, c) - lo) > (c - o).abs()
    buy_raw = (h > h.shift(1)) & (lo >= lo.shift(1)) & (c > o) & ~doji
    sell_raw = (lo < lo.shift(1)) & (h <= h.shift(1)) & (c < o) & ~doji
    buy = (buy_raw & ~buy_raw.shift(1, fill_value=False)).to_numpy()
    sell = (sell_raw & ~sell_raw.shift(1, fill_value=False)).to_numpy()
    frac = (_atr(bars_df, int(p["atr_len"])) / c).to_numpy()
    loc = bars_df.index.tz_convert(p["session_tz"])
    allowed = np.asarray((loc.hour != 0) & (loc.hour < 19))
    day = np.asarray(loc.normalize().tz_localize(None))
    o, h, lo = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, 0.0, 0.0
    last_day, tp_hit = None, False
    for i in range(m):
        if day[i] != last_day:
            last_day, tp_hit = day[i], False
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + t_)):
                tp_hit = tp_hit or h[i] >= e * (1 + t_)
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - t_)):
                tp_hit = tp_hit or lo[i] <= e * (1 - t_)
                pos = 0
        if pos == 0 and allowed[i] and not tp_hit and i + 1 < m and not np.isnan(frac[i]):
            if buy[i]:
                le[i], pos, entry_i = True, 1, i + 1
            elif sell[i]:
                se[i], pos, entry_i = True, -1, i + 1
            if pos != 0:
                s_, t_ = p["sl_k"] * frac[i], p["tp_k"] * frac[i]
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_k"] * a, "tp_stop": p["tp_k"] * a}


def portfolio_kwargs(**params):
    return {}
