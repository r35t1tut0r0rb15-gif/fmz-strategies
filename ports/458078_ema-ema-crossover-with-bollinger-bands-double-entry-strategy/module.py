"""EMA 12 / 26 crossings and Bollinger 55 / 0.9 breakouts, daily bars, long only: the EMA cross up, or a close breaking over the upper band in an EMA uptrend, buys with a stop 1 ATR under the signal close; the EMA cross down sells; after a stop-out a new upper-band breakout re-enters with the same stop level until the EMA cross down resets.
Port of FMZ strategy #458078 "EMA交叉与布林带双重入场策略结合趋势跟踪与波动突破的量化交易系统EMA-Crossover-with-Bollinger-Bands-Double-Entry-Strategy-A-Quantitative-Trading-System-Combining-Trend-Following-and-Volatility-Breakout" (EMA Crossover with BB Double Entry).

FMZ source id: 458078

Source
    https://www.fmz.com/strategy/458078 (PineScript v5, FMZ last modified 2024-07-29 17:14:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 195-318), EMA 12 / 26; ATR 14 x 1 stop from the signal close; BB 55, 0.9 sd; pause / resume off; add-on entry Long_BB (pyramiding 1)
    (crossover(ema12, ema26) or (bb breakout and ema12 > ema26)) and not inPosition -> stopLoss = close - atr, inPosition, entry Long
    inPosition and bb breakout and ema12 > ema26 -> entry Long_BB;  crossunder(ema12, ema26) -> close_all, inPosition = false, stopLoss = na
    while long: exit(Long / Long_BB, stop = stopLoss)

Interpretation choices (Pine rules in SURVEY_README.md)
    * inPosition is reset only by the EMA cross down, not by the stop: after a stop-out the "Long" entry
      stays blocked and the Long_BB entry (the same breakout test) re-enters, with the stop level of the
      last "Long" signal. With the default pyramiding of 1 a Long_BB entry fills only from flat. The
      loop follows the stop beside the signals: the stop is sent at the fill as the fraction 1 - level /
      fill open (known at the fill bar's open) and is taken from the fill bar (the source sends it from
      the bar after the fill, a one-bar difference). When the level is already at or over the fill open,
      the stop is marketable: the trade is closed at the next open, sent as a bar-close exit. Pause /
      resume is off by default. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily
      bars: mark coarse_bar_stop. The equity-risk position sizes are not ported (sizing is the
      optimisation layer's). FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fixed stop level as a fraction of the fill.
    2 generic: PASS, EMA crossings and band breakouts with an ATR stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: equity-risk position sizes stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458078_ema12_26_cross_bb_breakout_atr_stop_reentry_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [12, 9],
    "slow": [26, 21],
    "atr_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "atr_mult": 1.0, "atr_len": 14, "bb_len": 55, "bb_mult": 0.9}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    fe = c.ewm(span=int(p["fast"]), adjust=False).mean()
    sw = c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["bb_len"])
    upper = c.rolling(n).mean() + float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    brk = ((c > upper) & (c.shift(1) <= upper.shift(1))).to_numpy()
    bull = (fe > sw).to_numpy()
    lcond = ((fe > sw) & (fe.shift(1) <= sw.shift(1))).to_numpy()
    scond = ((fe < sw) & (fe.shift(1) >= sw.shift(1))).to_numpy()
    stop_new = (c - float(p["atr_mult"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sent = np.full(m, np.nan)                    # stop level sent with each entry, on its signal bar
    pos, pend, in_pos, level, active = 0, 0, False, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos, pend, active = 1, 0, np.nan
            if not np.isnan(level):
                if level < ov[i]:
                    active = level
                else:
                    lx[i], pend = True, 2        # stop already through the fill: closed at the next open
        elif pend == 2:
            pos, pend, active = 0, 0, np.nan
        if pos == 1 and not np.isnan(active) and lv[i] <= active:
            pos, active = 0, np.nan              # the stop fills inside this bar
        go = False
        if (lcond[i] or (brk[i] and bull[i])) and not in_pos:
            level, in_pos, go = stop_new[i], True, True
        if in_pos and brk[i] and bull[i]:
            go = True                            # Long_BB: fills only from flat (pyramiding 1)
        if go and pos == 0 and pend == 0:
            le[i], pend, sent[i] = True, 1, level
        if scond[i]:
            if pos == 1 and pend == 0:
                lx[i], pend = True, 2
            in_pos, level = False, np.nan
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(sent, index=ix)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, _ = _run(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = 1 - _run(bars_df, p)[2].shift(1) / bars_df["open"]     # the signal bar's level, as a fraction of the fill open
    return {"sl_stop": f.where(f > 0)}                          # at or through the fill: closed by a bar-close exit


def portfolio_kwargs(**params):
    return {}
