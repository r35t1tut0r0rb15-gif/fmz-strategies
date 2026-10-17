"""Chandelier Exit direction flips with a small fixed bracket, broker days: when the Chandelier Exit (22, 3, on closes)
turns up the strategy goes long, when it turns down short; each trade has a 30-"pip" stop and a 50-"pip" target from
the signal close (as ATR multiples).
Port of FMZ strategy #484924 "多重技术指标黄金即时变动检测与风险管理策略-Multi-Technical-Indicator-Gold-Real-Time-Movement-Detection-and-Risk-Management-Strategy" (1 Min Gold Heikin Ashi Strategy).

FMZ source id: 484924

Source
    https://www.fmz.com/strategy/484924 (PineScript v5, FMZ last modified 2025-03-05 10:35:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 182-641), Chandelier Exit 22 x 3 (closes), expiry 3, alternate signals on,
TP 50 / SL 30 "pips" x 0.1 (5 / 3 price units); all confirmation filters off by default
    longStop = highest(close, 22) - 3 ATR, ratcheted while close[1] > its previous value (shortStop mirrored)
    dir = close > shortStopPrev ? 1 : close < longStopPrev ? -1 : dir
    longcond_withexpiry = dir == 1 and the run of dir == 1 is <= 3 bars;  alternate: longCondition needs the previous
    signal state -1 (CondIni) -> entry long + exit(limit = close + 5, stop = close - 3) (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the filters off and alternate signals on, a long fires exactly on the bar dir turns from -1 to 1 and a short
      on the bar it turns from 1 to -1 (the first run after the start sets the state without a trade).
    * Criterion 2: on the author's daily ETH_USDT (daily ATR about 120) 3 / 5 price units are about 0.025 / 0.04
      Wilder ATR(14) (judgement before any backtest): sl_atr x ATR, the target 5 / 3 times that, fixed at the signal
      bar (shifted one bar inside stops(), re-based on the fill). The signals alternate, so no same-side re-placement.
    * The MA lines, SuperTrend, STC and dashboard are display or disabled filters (the MA lines would be VWMA only as
      an option). Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header (the
      "1 Min Gold" title is a label): coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: ADAPT, price-unit distances -> ATR multiples; ATR channel.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_484924_chandelier_flip_small_bracket"
FAMILY = "chandelier_exit"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.025, 1.0],
    "ce_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"ce_length": 22, "ce_mult": 3.0, "sl_atr": 0.025, "tp_ratio": 1.6667, "atr_len": 14}  # tp_ratio: 50 / 30 pips


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _ce_dir(bars_df, n, mult):
    c = bars_df["close"]
    a = (mult * _atr(bars_df, n)).to_numpy()
    hc, lc = c.rolling(n).max().to_numpy(), c.rolling(n).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    out = np.ones(m, dtype=np.int8)
    ls_p = ss_p = np.nan
    d = 1
    for i in range(m):
        ls, ss = hc[i] - a[i], lc[i] + a[i]
        lsp = ls if np.isnan(ls_p) else ls_p              # nz(longStop[1], longStop)
        ssp = ss if np.isnan(ss_p) else ss_p
        c1 = cv[i - 1] if i > 0 else np.nan
        ls = max(ls, lsp) if c1 > lsp else ls
        ss = min(ss, ssp) if c1 < ssp else ss
        if cv[i] > ssp:
            d = 1
        elif cv[i] < lsp:
            d = -1
        out[i] = d
        ls_p, ss_p = ls, ss
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = _ce_dir(bars_df, int(p["ce_length"]), float(p["ce_mult"]))
    d1 = np.concatenate(([1], d[:-1]))
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series((d == 1) & (d1 == -1), index=idx), false, pd.Series((d == -1) & (d1 == 1), index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
