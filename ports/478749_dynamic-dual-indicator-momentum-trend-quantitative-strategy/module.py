"""Broker days: the SMA 9 crossing over the SMA 21 with RSI 14 under 50 goes long, crossing under with RSI over 50 goes short, each with a 2 % stop and a 4 % target from the signal close; a long closes on a crossing under or an RSI over 50, a short on a crossing over or an RSI under 50; reversing.
Port of FMZ strategy #478749 "Dynamic Dual Indicator Momentum Trend Quantitative Strategy System" (RSI-MA Synergy).

FMZ source id: 478749

Source
    https://www.fmz.com/strategy/478749 (PineScript v5, FMZ last modified 2025-01-17 16:41:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 87-150), SMA 9 / 21; RSI 14 vs 50; SL 2 %, TP 4 %; volume and volatility filters off by default
    longCondition = crossover(fastMA, slowMA) and rsi < 50 -> entry Long, exit(stop = close x 0.98, limit = close x 1.04);  shortCondition mirrored
    position_size > 0 and (crossunder(fastMA, slowMA) or rsi > 50) -> close Long;  position_size < 0 and (crossover or rsi < 50) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume and volatility filters default to off, so volume is not used (held for volume, not
      used). The bracket is sent on signal bars only, as levels from that close: ported as fractions of
      the fill, exact (1e-6 floor). The closes test the position held at the bar's close, so they act
      from the bar after the fill and only on a position the bar's entries leave unchanged; an opposite
      entry reverses. REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, SMA crossings against the RSI side, RSI-midline exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_478749_sma9_21_cross_rsi50_2_4pct_bracket_rsi_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.02, 0.03],
    "tp": [0.04, 0.06],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "sl": 0.02, "tp": 0.04}


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
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    r = _rsi(c, 14)
    xo = (f > s) & (f.shift(1) <= s.shift(1))
    xu = (f < s) & (f.shift(1) >= s.shift(1))
    buy, sell = (xo & (r < 50)).to_numpy(), (xu & (r > 50)).to_numpy()
    ex_l, ex_s = (xu | (r > 50)).to_numpy(), (xo | (r < 50)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    sl, tp = float(p["sl"]), float(p["tp"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl))
            .mask(sf, k * (1 + sl) - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
