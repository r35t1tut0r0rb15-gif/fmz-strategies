"""Broker days: with the EMA 20 above the EMA 90, a green hammer-like candle (lower shadow at least 0.8 x the body) opens a long; with EMA 20 under EMA 90, a red shooting-star-like candle with RSI 14 at or over 70 opens a short; the script's own flag closes it on a close 2.5 % through the entry, judged by the trend of the closing bar (as written).
Port of FMZ strategy #483680 "Exponential Moving Average Candle Stop Trading Strategy" (Advanced Candle Stop Strategy Backtest - Tuned v9).

FMZ source id: 483680

Source
    https://www.fmz.com/strategy/483680 (PineScript v6, FMZ last modified 2025-02-25 11:11:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 162-276), EMA 5 / 20 / 90; support / resistance 30 (incl. the bar); candle-stop shadows 0.8 x body; stop 2.5 % (close-checked); TP 7 % / 6 % with RR >= 3; risk-based qty
    trend = ema20 > ema90 ? "up" : ema20 < ema90 ? "down" : "neutral";  breakout_detected (close beyond the 30-bar extreme that includes the bar) never becomes true
    position == 0 and is_candle_stop(trend): up -> stop := close x 0.975, entry Long, position := amount, entry_price := close;  down -> stop := close x 1.025, (rsi >= 70) entry Short ...
    position > 0: (trend up and (tp_long or close <= stop)) or (trend down and (tp_short or close >= stop)) -> close("Long") if trend up else close("Short"), position := 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The breakout flag compares the close with a 30-bar high / low that includes the bar, so it never
      turns on and entries are always allowed. The take-profit tests need a reward / risk of 3 computed
      as profit / (-profit), which is -1, so they never fire: trades end only by the close-checked 2.5 %
      stop or a reversal. The exit block picks its side from the CURRENT trend, not the open trade: a long
      in a "down" bar tests the short stop (close above the long's stop) and closes "Short" (nothing), but
      the script's flag still resets, so the long stays open while the script looks flat (weird case;
      followed in the loop). A bar with no clear trend checks nothing. Closes fill at the next open. The
      risk-based quantity is sizing. REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked stop in the signals.
    2 generic: PASS, trend-side candle-stop reversals with a close-based stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based qty stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483680_candle_stop_trend_close_stop_flag_reversal"
FAMILY = "candlestick_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_pct": [0.025, 0.05],
    "shadow": [0.8, 1.0],
}
DEFAULT_PARAMS = {"stop_pct": 0.025, "shadow": 0.8}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e20, e90 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=90, adjust=False).mean()
    trend = np.where(e20 > e90, 1, np.where(e20 < e90, -1, 0))
    body = (c - o).abs()
    up_s, lo_s = h - np.maximum(o, c), np.minimum(o, c) - lo
    k = float(p["shadow"])
    cs_up = ((lo_s >= k * body) & (up_s < body) & (c > o)).to_numpy()
    cs_dn = ((up_s >= k * body) & (lo_s < body) & (c < o)).to_numpy()
    r = _rsi(c, 14).to_numpy()
    cn = c.to_numpy(dtype=float)
    sp = float(p["stop_pct"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, flag, stop = 0, False, np.nan
    for i in range(m):
        held = tgt                          # the real position after this bar's open
        new = held
        if not flag:
            if trend[i] == 1 and cs_up[i]:
                stop, flag = cn[i] * (1 - sp), True
                new = 1
            elif trend[i] == -1 and cs_dn[i]:
                stop = cn[i] * (1 + sp)
                if r[i] >= 70:
                    flag, new = True, -1
        if flag:
            if trend[i] == 1 and cn[i] <= stop:
                if held == 1 and new == held:
                    new = 0                 # close("Long")
                flag = False
            elif trend[i] == -1 and cn[i] >= stop:
                if held == -1 and new == held:
                    new = 0                 # close("Short")
                flag = False
        if new != held and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif held == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
