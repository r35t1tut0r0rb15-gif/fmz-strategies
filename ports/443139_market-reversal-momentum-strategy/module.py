"""SuperTrend(10, 2) flips down on a falling Fisher transform above 2.5, 2-minute bars, short only: the flip on such a bar goes short; a close at or over the signal close + 2 ATR, or at or under the
signal close - 2 ATR, closes.
Port of FMZ strategy #443139 "Market Reversal Momentum Strategy" (Supertrend and Fisher_SHORT).

FMZ source id: 443139

Source
    https://www.fmz.com/strategy/443139 (PineScript v5, FMZ last modified 2024-02-29 15:10:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-222), Fisher length 10 on hl2; SuperTrend ATR 10 x 2 on hl2 (Wilder ATR); risk amount (sizing); qty 1
    fish1 = Fisher(hl2, 10);  durum = -1 when fish1 > 2.5 and fish1[1] > fish1;  sellSignal = trend flips down and durum == -1 -> entry Sell (qty 1)
    on the signal: stopLoss = close + 2 atr, takeProfit = close - 2 atr;  close >= stopLoss -> close;  else close <= takeProfit -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are bar-close tests of the close against the levels set on the latest signal bar
      (later signals re-set them, as written), filled at the next open. takeProfit2 / 3 and the contract
      count only plot. The Fisher value and line follow the script's nz seeds. Short only. The quantity 1
      is sizing. FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend flip with a Fisher extreme.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430988 (2 members, best partner #430988, Jaccard 0.696); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443139_supertrend_flip_fisher_extreme_short"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [2.0, 3.0],
    "fisher_level": [2.5, 1.5],
}
DEFAULT_PARAMS = {"multiplier": 2.0, "fisher_level": 2.5, "length": 10, "periods": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    n = int(p["length"])
    hi_, lo_ = hl2.rolling(n).max().to_numpy(), hl2.rolling(n).min().to_numpy()
    hv2 = hl2.to_numpy(dtype=float)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    mult = float(p["multiplier"])
    atr = _rma(tr, int(p["periods"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    fl = float(p["fisher_level"])
    fish = np.zeros(m)
    val = 0.0
    up_p = dn_p = np.nan
    d, d_prev = 1, 1
    trend = np.ones(m, dtype=np.int8)
    sell = np.zeros(m, dtype=bool)
    for i in range(m):
        rng = hi_[i] - lo_[i]
        raw = 0.66 * ((hv2[i] - lo_[i]) / rng - 0.5) + 0.67 * val if rng and not np.isnan(rng) else np.nan
        prev_f = fish[i - 1] if i > 0 and not np.isnan(fish[i - 1]) else 0.0     # nz(fish1[1])
        if not np.isnan(raw):
            val = 0.999 if raw > 0.99 else (-0.999 if raw < -0.99 else raw)
            fish[i] = 0.5 * np.log((1 + val) / (1 - val)) + 0.5 * prev_f
        else:
            val = 0.0                                                            # nz(value[1]) next bar
            fish[i] = np.nan
        u, dd = hv2[i] - mult * atr[i], hv2[i] + mult * atr[i]
        u1 = u if np.isnan(up_p) else up_p
        d1 = dd if np.isnan(dn_p) else dn_p
        if i > 0 and cv[i - 1] > u1 and not np.isnan(u):
            u = max(u, u1)
        if i > 0 and cv[i - 1] < d1 and not np.isnan(dd):
            dd = min(dd, d1)
        d_prev = d
        if d == -1 and cv[i] > d1:
            d = 1
        elif d == 1 and cv[i] < u1:
            d = -1
        trend[i] = d
        up_p, dn_p = u, dd
        f1 = fish[i - 1] if i > 0 else np.nan
        durum = (not np.isnan(fish[i])) and fish[i] > fl and (not np.isnan(f1)) and f1 > fish[i]
        sell[i] = d == -1 and d_prev == 1 and durum
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, sl, tp = False, np.nan, np.nan
    for i in range(m):
        if sell[i] and not np.isnan(atr[i]):
            sl, tp = cv[i] + atr[i] * mult, cv[i] - atr[i] * mult
            if not held:
                se[i] = True
        elif held and (cv[i] >= sl or cv[i] <= tp):
            sx[i] = True
        held = (held and not sx[i]) or se[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
