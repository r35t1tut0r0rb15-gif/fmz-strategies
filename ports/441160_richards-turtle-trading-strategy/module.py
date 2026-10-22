"""Turtle-style 20-bar closing breakouts with a state flag, broker days: from an untraded state, the close above the previous 20-bar closing high goes long, under the 20-bar closing low short; a long
closes under its 4 x EMA(ATR 20) stop or the 10-bar closing low; the short's flag clears on its own bar, as written.
Port of FMZ strategy #441160 "Richards Turtle Trading Strategy" (Richard Strategy).

FMZ source id: 441160

Source
    https://www.fmz.com/strategy/441160 (PineScript v4, FMZ last modified 2024-02-06 11:56:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-185), stop loss var 4; length 20 (10 for the exits); ATR 20, EMA 20 of it
    buyCon = close > highest(close[1], 20) and traded false -> entry long, traded, buy, stoploss = round(close - 4 ema(atr(20), 20))
    sellCon = close < lowest(close[1], 20) and traded false -> entry short, traded, sell, stoploss = round(close - 4 ema(atr20))
    traded: buy and (close < stoploss or close < lowest(close[1], 10)) -> close long, untraded;  sell and (close > stoploss or close > highest(close[1], 10)) -> close short, untraded

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported as written. The short's stop is also set below the close, so on the short's own signal bar
      the close is above it: the close of "short" is sent while the position is still flat (it acts only on
      a held position, so the entry stands) and the flag returns to untraded. The open short is therefore
      closed only on a later short signal (its close then finds the short held) or reversed by a long
      signal. A long is tracked by the flag and exits on its stop or the 10-bar low. round() rounds half
      away from zero. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, closing-price channels and the ATR stop test.
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

NAME = "fmz_441160_turtle_close_channel_flag_state"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "stop_mult": [4, 2],
}
DEFAULT_PARAMS = {"length": 20, "stop_mult": 4, "atr_len": 20}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    c1 = c.shift(1).fillna(0.0)
    hh, ll = c1.rolling(n).max().to_numpy(), c1.rolling(n).min().to_numpy()
    hh2, ll2 = c1.rolling(n // 2).max().to_numpy(), c1.rolling(n // 2).min().to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    ea = _rma(tr, int(p["atr_len"])).ewm(span=20, adjust=False).mean().to_numpy()
    k = float(p["stop_mult"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, traded, side, stop = 0, False, "none", 0.0
    for i in range(m):
        new = held
        if cv[i] > hh[i] and not traded:
            new, traded, side = 1, True, "buy"
            stop = np.floor(cv[i] - k * ea[i] + 0.5)
        if cv[i] < ll[i] and not traded:
            new, traded, side = -1, True, "sell"
            stop = np.floor(cv[i] - k * ea[i] + 0.5)
        if traded:
            if side == "buy" and (cv[i] < stop or cv[i] < ll2[i]):
                if held == 1 and new == 1:
                    new = 0
                traded = False
            if side == "sell" and (cv[i] > stop or cv[i] > hh2[i]):
                if held == -1 and new == -1:
                    new = 0
                traded = False
        tgt[i] = new
        held = new
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
