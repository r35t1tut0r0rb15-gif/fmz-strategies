"""RSI momentum with widening bands, broker days: the RSI 14 above 70 while the 20-day deviation is not shrinking goes long, under 30 short; the close under the SMA 50 closes a long, above it a short;
reversing.
Port of FMZ strategy #440809 "基于布林带RSI和移动平均线的趋势跟踪策略Trend-Following-Strategy-Based-on-Bollinger-Bands-RSI-and-Moving-Average" (Bollinger Bands, RSI, and MA Strategy).

FMZ source id: 440809

Source
    https://www.fmz.com/strategy/440809 (PineScript v5, FMZ last modified 2024-02-02 11:35:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-193), BB 20 / 2 (and 1, plotted); RSI 14 (70 / 30); MA 50; stop loss input unused
    enterLong = rsi > 70 and not (stdev < stdev[1]);  enterShort = rsi < 30 and not contracting;  exitLong = close < sma50;  exitShort = close > sma50
    held long and exitLong -> close Long;  held short and exitShort -> close Short;  then the entries;  then exitLong -> close Long, exitShort -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in the written order: the closes written before the entries act on the held
      position; those written after them act only on a held position, so a reversing entry stands (as
      #438020). The stop-loss input is never used. Pine's stdev is the population deviation.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels, deviation slope and SMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440809_rsi_momentum_widening_bands_ma_exit"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [50, 20],
    "overbought": [70, 60],
}
DEFAULT_PARAMS = {"ma_len": 50, "overbought": 70, "b_len": 20, "rsi_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sd = c.rolling(int(p["b_len"])).std(ddof=0)
    widen = ~(sd < sd.shift(1))
    r = _rsi(c, int(p["rsi_len"]))
    ob = float(p["overbought"])
    L = ((r > ob) & widen).to_numpy()
    S = ((r < 100 - ob) & widen).to_numpy()
    ma = c.rolling(int(p["ma_len"])).mean()
    XL, XS = (c < ma).to_numpy(), (c > ma).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos > 0 and XL[i]:
            new = 0
        if pos < 0 and XS[i]:
            new = 0
        if L[i]:
            new = 1
        if S[i]:
            new = -1
        if XL[i] and pos == 1 and new == 1:
            new = 0
        if XS[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
