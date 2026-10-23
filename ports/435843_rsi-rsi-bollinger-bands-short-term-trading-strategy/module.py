"""Broker days: the RSI 14 crossing over the lower band of a volume-weighted RSI channel (centre 0.6 x the volume-weighted EMA 25 of the RSI + 20, width 2 sd of the RSI over 25) goes long, crossing under the upper band goes short; a long whose close falls under 94 % of its signal close is turned into a short signal; reversing.
Port of FMZ strategy #435843 "RSI与布林带结合的短线交易策略RSI-Bollinger-Bands-Short-term-Trading-Strategy" (rsi+bb st).

FMZ source id: 435843

Source
    https://www.fmz.com/strategy/435843 (PineScript v3, FMZ last modified 2023-12-19 11:31:09).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 135-194), RSI 14; band length 25, multiplier 20 / 10 = 2; centre ratio 0.6; stop rate 94 %
    bbc = 0.6 x ema(rsi x volume, 25) / ema(volume, 25) + 20;  bbg = 2 stdev(rsi, 25);  lc = crossover(rsi, bbc - bbg);  sc = crossunder(rsi, bbc + bbg)
    last_pos = lc ? 1 : last_pos[1]; sc -> 2;  last_price = close when last_pos turns 1;  last_pos == 1 and close < last_price x 0.94 -> lc := false, sc := true;  lc -> entry long, sc -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel centre is volume-weighted (vwma_e) and pulled toward 50, as written. The 6 % "stop" is
      a bar-close test that sends the SHORT entry (a reversal, not a flat exit), as written. A comparison
      with na is false, so the first long after the start keeps no stop price until last_pos has been set
      once (weird case). No sizing code. REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop as a reversal signal.
    2 generic: PASS, RSI against a volume-weighted RSI channel.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the channel centre ema(rsi x volume, 25) / ema(volume, 25); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435843_rsi_volume_weighted_channel_cross_stop_flip_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_bb": [25, 50],
    "sl": [0.94, 0.97],
}
DEFAULT_PARAMS = {"len_rsi": 14, "len_bb": 25, "mult": 2.0, "ratio": 0.6, "sl": 0.94}


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
    c, v = bars_df["close"], bars_df["volume"]
    rsi = _rsi(c, int(p["len_rsi"]))
    n = int(p["len_bb"])
    ev = v.ewm(span=n, adjust=False).mean()
    bbc = (rsi * v).ewm(span=n, adjust=False).mean() / ev.where(ev != 0)
    r = float(p["ratio"])
    bbc = bbc * r + 50 * (1 - r)
    bbg = rsi.rolling(n).std(ddof=0) * float(p["mult"])
    bbu, bbl = bbc + bbg, bbc - bbg
    lc = ((rsi > bbl) & (rsi.shift(1) <= bbl.shift(1))).to_numpy()
    sc = ((rsi < bbu) & (rsi.shift(1) >= bbu.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = float(p["sl"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lp_prev, lpr = np.nan, np.nan
    for i in range(m):
        l_i, s_i = lc[i], sc[i]
        lp = 1.0 if l_i else lp_prev
        if s_i:
            lp = 2.0
        if (lp_prev != 1.0 and not np.isnan(lp_prev)) and lp == 1.0:
            lpr = cv[i]
        if lp == 1.0 and cv[i] < lpr * k:
            l_i, s_i, lp = False, True, 2.0
        le[i], se[i] = l_i, s_i
        lp_prev = lp
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
