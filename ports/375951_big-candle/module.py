"""Big candles (range over 1.8 x its 120-bar average, volume over 2.7 x its 200-bar average) in the candle's direction beyond the EMA 50, with ADX (DI 7, smoothing 26) between 30 and 50 and a SuperTrend 2 / 10 agreeing: up candles go long, down candles go short, each with a 1.3 % target and 9 % stop from the entry; reversing.
Port of FMZ strategy #375951 "Big-candle分享" (Big candle).

FMZ source id: 375951

Source
    https://www.fmz.com/strategy/375951 (PineScript v5, FMZ last modified 2022-08-02 14:31:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 39-115), range x 1.8 over 120 bars; volume x 1.8 x 1.5 over 200 bars; EMA 50; DMI 7 / 26, ADX 30-50; SuperTrend 2 / 10; TP 1.3 %, SL 9 % of the avg price; backtest window 2022 .. 2220
    bull = close > open and close > ema50 and high - low > avg range x 1.8 and 30 < adx < 50 and volume > avg volume x 2.7 and direction == -1;  bear mirror (direction == 1)
    usedBu := true on a bull bar (reset when the SuperTrend direction changes);  bull and usedBu -> entry L;  bear and usedBe -> entry S;  exit(profit 1.3 %, loss 9 % of the avg price)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The used-candle flag is set on the bull bar itself before the entry test, so every bull bar (not
      only the first of a SuperTrend leg) enters, as written; repeats while long are ignored. The author's
      date window is dropped like other date windows (2022 .. 2220; the C118-C124 reading). The percent
      exits are a scalar bracket from the fill (as #440797). No backtest header names a bar size and no
      input does: FREQ = "bar_size_pending"; the bars come from the house bar_sizes.build_bars with the
      driver's bar_size (it keeps the volume). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). The 100 % of equity size, capital and commission are sizing / costs, not ported. The
      source carries the Mozilla Public License 2.0 notice.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, volume-confirmed big candles with trend filters.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: 100 % of equity, capital 10000 and commission 0.04 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar by the house bar builder) in volume > sum(volume, 200) / 200 x 2.7; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2022 .. 2220 window dropped).
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_375951_big_candle_volume_ema50_adx_supertrend_pct_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "multiplier": [1.8, 1.5],
    "lookback": [120, 60],
}
DEFAULT_PARAMS = {"multiplier": 1.8, "lookback": 120, "di_len": 7, "adx_len": 26, "tp": 0.013, "sl": 0.09}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n, nsig):
    """Pine ta.dmi(n, nsig): DI over n bars, ADX smoothed over nsig."""
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), nsig)
    return plus, minus, adx


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    k = float(p["multiplier"])
    avg_rng = (h - lo).rolling(int(p["lookback"])).mean() * k
    avg_vol = v.rolling(200).mean() * k * 1.5
    ema = c.ewm(span=50, adjust=False).mean()
    adx = _dmi(bars_df, int(p["di_len"]), int(p["adx_len"]))[2]
    d = _supertrend(bars_df, 2.0, 10)[1]
    base = (h - lo > avg_rng) & (adx > 30) & (adx < 50) & (v > avg_vol)
    le = (c > o) & (c > ema) & base & (d == -1)
    se = (c < o) & (c < ema) & base & (d == 1) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
