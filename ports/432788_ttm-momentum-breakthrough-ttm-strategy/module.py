"""TTM-squeeze momentum bursts with five-bar time exits, broker days: with the 20-bar Bollinger band outside the Keltner
channel, the RSI 30 between 50.5 and 70, a jump of the band-position index above 0.15 and the TTM momentum above zero,
the first such bar goes long and the trade closes five bars after its signal; the mirror goes short.
Port of FMZ strategy #432788 "动量突破TTM策略Momentum-Breakthrough-TTM-Strategy" (EA_Binary Option Spfrat Strategy).

FMZ source id: 432788

Source
    https://www.fmz.com/strategy/432788 (PineScript v4, FMZ last modified 2023-11-21 15:07:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 134-187), TTM 20, BB 50 x 0.2, RSI 30, levels 50.5 / 70 and 49.5 / 30, impulse 0.15, momentum +-0.001
    conso = bband(20, 2) - keltner(20, 1) >= 0;  osc = linreg(close - e1 / 2, 20, 0) (as the TTM port #432215)
    bbr = beyond the 50 x 0.2 band ? (close - band) / width / 10 : 0.05;  bbi = bbr - bbr[1]
    long1 = rsi30 in (50.5, 70) and bbi > 0.15 and osc > 0.001 and conso;  long = long1 turns on -> entry long;  long[5] -> close long
    mirror (rsi30 in (30, 49.5), bbi < -0.15, osc < -0.001) -> entry short;  short[5] -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the momentum thresholds +-0.001 are price units (about 0 ATR on daily BTC): ported
      as osc_atr x Wilder ATR 14 with 0 (a sign test, as written in effect) and 0.1 in the grid.
    * The closes five bars after the signal are explicit time exits from simulate(); they act on the
      position held at the bar's start. pyramiding 1999 lets repeated signals add (criterion 4, not
      ported); the close then takes the whole side, as written. The short entry is written first, the
      long second. strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; explicit time exits.
    2 generic: ADAPT, price-unit momentum thresholds -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 1999 and the initial capital stored in original_sizing.txt.
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

NAME = "fmz_432788_ttm_squeeze_burst_time_exit"
FAMILY = "volatility_squeeze"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "osc_atr": [0.0, 0.1],
    "hold": [5, 3],
}
DEFAULT_PARAMS = {"ttm_len": 20, "bb_len": 50, "bb_mult": 0.2, "rsi_len": 30, "impulse": 0.15, "atr_len": 14,
                  "osc_atr": 0.0, "hold": 5}


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


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ttm_len"])
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    bb = c.rolling(n).mean() + 2 * c.rolling(n).std(ddof=0)
    kc = c.ewm(span=n, adjust=False).mean() + tr.ewm(span=n, adjust=False).mean()
    conso = (bb - kc) >= 0
    e1 = (h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()
    osc = _linreg(c - e1 / 2, n)
    d = c.diff()
    ru = d.clip(lower=0).ewm(alpha=1 / int(p["rsi_len"]), adjust=False).mean()
    rd = (-d.clip(upper=0)).ewm(alpha=1 / int(p["rsi_len"]), adjust=False).mean()
    rsi = (100 - 100 / (1 + ru / rd)).where(rd != 0, 100.0).where(~((ru == 0) & (rd != 0)), 0.0)
    m_ = int(p["bb_len"])
    basis = c.rolling(m_).mean()
    dev = float(p["bb_mult"]) * c.rolling(m_).std(ddof=0)
    up_, dn_ = basis + dev, basis - dev
    w = up_ - dn_
    bbr = pd.Series(np.where(c > up_, (c - up_) / w / 10, np.where(c < dn_, (c - dn_) / w / 10, 0.05)),
                    index=c.index).where(basis.notna())
    bbi = bbr - bbr.shift(1).fillna(0.0)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    th = float(p["osc_atr"]) * atr
    imp = float(p["impulse"])
    l1 = (rsi > 50.5) & (rsi < 70) & (bbi > imp) & (osc > th) & conso
    s1 = (rsi < 49.5) & (rsi > 30) & (bbi < -imp) & (osc < -th) & conso
    lg = (l1 & ~l1.shift(1, fill_value=False)).to_numpy()
    sh = (s1 & ~s1.shift(1, fill_value=False)).to_numpy()
    k = int(p["hold"])
    lc = np.concatenate((np.zeros(k, dtype=bool), lg[:-k])) if len(lg) > k else np.zeros(len(lg), dtype=bool)
    sc = np.concatenate((np.zeros(k, dtype=bool), sh[:-k])) if len(sh) > k else np.zeros(len(sh), dtype=bool)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if sh[i]:
            pos = -1
        if lg[i]:
            pos = 1
        if lc[i] and start == 1 and pos == 1:
            pos = 0
        if sc[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
