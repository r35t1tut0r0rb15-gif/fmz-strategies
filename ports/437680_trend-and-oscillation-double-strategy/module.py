"""One-minute bars: the script's own Trend Surfers state (a 168-bar breakout opens a virtual trade with an 8 x ATR 10 ratcheting trail and a 2 x ATR fixed stop) gives a trail line; the trail under the 168-bar lowest low on a rising close with +DI above -DI (Mawreez trend oscillator) goes long, the trail above the 168-bar highest high on a falling close with -DI above +DI goes short; a 100 % target; reversing.
Port of FMZ strategy #437680 "Trend and Oscillation Double Strategy" (Strategy Myth-Busting #8 - TrendSurfers+TrendOsc - [MYN]).

FMZ source id: 437680

Source
    https://www.fmz.com/strategy/437680 (PineScript v5, FMZ last modified 2024-01-04 17:32:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 178-520), highest / lowest 168; trailing ATR 10 x 8; fixed ATR 10 x 2; trend oscillator DI 14, sensitivity 25; ADX off; TP1 100 % (100 % of position); SL 999 %
    inTrade: 0 -> +-1 on crossover(close, highest(high, 168)[1]) / crossunder(close, lowest(low, 168)[1]);  1 -> 0 on the short breakout or low <= max(fixedStopLine[1], longTrailingStop);  mirror
    trailingStopLine = inTrade 1 ? longTrailingStop (max of close - 8 atr) : inTrade -1 ? shortTrailingStop : na;  long = trail < lowestLow and close > close[1] and plus_di > minus_di -> entry Long (not in a long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Trend Surfers part is only the script's internal state (its own entries and exits are
      commented out): it supplies the trail line used by the entry tests, run as written (the fixed stop
      is na on the bar after the virtual entry, so only the trail can end it there). The trend oscillator
      is the triple "lag-free" EMA smoothing of the rma DI ratios. TP1 is a full exit at +100 % from the
      average price (TP2-4 never come first); the 999 % close stop can never act. The alert string reads
      volume but no rule does: volume is not used (held for volume). REVERSAL INTENDED. The equity-based
      contracts are sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 100 % target from the fill.
    2 generic: PASS, breakout-trail state with a DI trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity / close x leverage 1, commission 0.075 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (date filters always true).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437680_trend_surfers_trail_state_trend_osc_1m_reversal"
FAMILY = "breakout_trail"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hl_period": [168, 100],
    "trail_mult": [8.0, 4.0],
}
DEFAULT_PARAMS = {"hl_period": 168, "trail_atr": 10, "trail_mult": 8.0, "fix_atr": 10, "fix_mult": 2.0,
                  "di_len": 14, "tp": 1.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _smooth(x, n):
    f28 = _ema(x, n)
    v_c = f28 * 1.5 - _ema(f28, n) * 0.5
    f38 = _ema(v_c, n)
    v10 = f38 * 1.5 - _ema(f38, n) * 0.5
    f48 = _ema(v10, n)
    return f48 * 1.5 - _ema(f48, n) * 0.5


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    n = int(p["hl_period"])
    hh = h.rolling(n).max().shift(1)
    ll = lo.rolling(n).min().shift(1)
    lcs = ((c > hh) & (c.shift(1) <= hh.shift(1))).to_numpy()
    scs = ((c < ll) & (c.shift(1) >= ll.shift(1))).to_numpy()
    tatr = (_rma(tr, int(p["trail_atr"])) * float(p["trail_mult"])).to_numpy()
    fatr = (_rma(tr, int(p["fix_atr"])) * float(p["fix_mult"])).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    trail = np.full(m, np.nan)
    in_t, lts, sts = 0, 0.0, 999999.9
    fixed_p = np.nan
    first_px = first_fx = np.nan
    for i in range(m):
        if (lcs[i] or scs[i]) and in_t == 0:
            in_t = 1 if lcs[i] else -1
            new_trade = True
        else:
            new_trade = False
        # math.max / math.min with an na fixed stop is na, and a comparison with na is false
        long_hit = (not np.isnan(fixed_p)) and lv[i] <= max(fixed_p, lts)
        short_hit = (not np.isnan(fixed_p)) and hv[i] >= min(fixed_p, sts)
        if in_t == 1 and (scs[i] or long_hit):
            in_t = 0
        elif in_t == -1 and (lcs[i] or short_hit):
            in_t = 0
        lts = max(cv[i] - tatr[i], lts) if in_t == 1 else 0.0
        sts = min(cv[i] + tatr[i], sts) if in_t == -1 else 999999.0
        fixed = np.nan
        if in_t != 0:
            if new_trade:
                first_px, first_fx = cv[i], fatr[i]
            fixed = first_px - first_fx if in_t == 1 else first_px + first_fx
            trail[i] = lts if in_t == 1 else sts
        fixed_p = fixed
    tl = pd.Series(trail, index=c.index)
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > 0) & (up > dn), up, 0.0), index=c.index)
    mdm = pd.Series(np.where((dn > 0) & (dn > up), dn, 0.0), index=c.index)
    k = int(p["di_len"])
    r1 = _rma(tr, k)
    pdi = _smooth(_rma(pdm, k) / r1, 3)
    mdi = _smooth(_rma(mdm, k) / r1, 3)
    long_c = (tl < ll) & (c > pc) & (pdi > mdi)
    short_c = (tl > hh) & (c < pc) & (pdi < mdi)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return long_c & ~short_c, false, short_c & ~long_c, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
