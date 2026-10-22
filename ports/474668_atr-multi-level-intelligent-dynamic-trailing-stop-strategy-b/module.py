"""First green candle after a red close under the Bollinger 20 / 1.5 lower band, daily bars, long only: it buys; a close 12 % under the signal close sells, and once the close reaches 20 % over the signal close or a green close reaches the upper band, a close-based ATR ratchet (close - ATR 20) sells when a close falls under it.
Port of FMZ strategy #474668 "基于布林带和ATR的多级智能动态跟踪止损策略-Multi-Level-Intelligent-Dynamic-Trailing-Stop-Strategy-Based-on-Bollinger-Bands-and-ATR" (Demo GPT - Bollinger Bands Strategy with Tightened Trailing Stops).

FMZ source id: 474668

Source
    https://www.fmz.com/strategy/474668 (PineScript v5, FMZ last modified 2024-12-11 14:52:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-242), BB SMA 20, 1.5 sd; ATR 20, multiplier 1.0; target trigger 20 %, stop 12 % of the signal close; 100 % of equity, commission 0.1 %, slippage 3
    close < lower and red -> flag;  flag and green -> entry Long, target := close x 1.2, stop := close x 0.88, trail := na, flag := false;  long: close >= target -> trail := max(trail, close - atr);  close < trail -> close Long;  close <= stop -> close Long;  close >= upper and green -> trail := max(trail, close - atr);  close < trail -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every exit is a bar-close test, so a loop follows the flag, the levels and the position in the
      written order: the levels are set on each signal bar (also a repeat while long, as written), the
      tests run only while a long is held into the bar, and every close resets the levels. Long only.
      The costs and the equity share are not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band-dip reversal candles with close-based stop and ATR ratchet.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size, commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474668_bb20_1p5_dip_green_close_stop_atr_ratchet_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "atr_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "atr_mult": 1.0, "mult": 1.5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = (basis + dev).to_numpy(dtype=float), (basis - dev).to_numpy(dtype=float)
    a = (_atr(bars_df, n) * float(p["atr_mult"])).to_numpy(dtype=float)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, flag = 0, 0, False
    tgt = stp = tr = np.nan

    def ratchet(t, v):
        return v if np.isnan(t) else max(t, v)

    for i in range(m):
        pos = nxt
        green, red = cv[i] > ov[i], cv[i] < ov[i]
        if cv[i] < dn[i] and red:
            flag = True
        if flag and green:
            if pos == 0 and nxt == 0:
                le[i], nxt = True, 1
            tgt, stp, tr, flag = cv[i] * 1.2, cv[i] * 0.88, np.nan, False
        if pos == 1 and not np.isnan(tgt) and cv[i] >= tgt:
            tr = ratchet(tr, cv[i] - a[i])
        if pos == 1 and not np.isnan(tr) and cv[i] < tr:
            if nxt == 1:
                lx[i], nxt = True, 0
            tgt = stp = tr = np.nan
        if pos == 1 and not np.isnan(stp) and cv[i] <= stp:
            if nxt == 1:
                lx[i], nxt = True, 0
            tgt = stp = tr = np.nan
        if pos == 1 and cv[i] >= up[i] and green:
            tr = ratchet(tr, cv[i] - a[i])
        if pos == 1 and not np.isnan(tr) and cv[i] < tr:
            if nxt == 1:
                lx[i], nxt = True, 0
            tgt = stp = tr = np.nan
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
