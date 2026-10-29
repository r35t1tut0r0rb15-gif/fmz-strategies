| Function | Module | Inputs | Outputs | Defaults | What / source |
|---|---|---|---|---|---|
| `adaptive_ls_trend` | extra_trend | close | trail, osc, ls | length=24, sc=0.2 | ``functionTrend`` of the FMZ "OCC Trend Combo" strategy (Josef Tainsh), |
| `adaptive_price_zone` | extra_hpotter | high, low, close | upper, lower, basis | periods=20, band_pct=2.0 | Lee Leibfarth's Adaptive Price Zone (TASC Sep 2006): double EMA of |
| `adaptive_trend_flow` | extra_trend | high, low, close | basis, upper, lower, trend, level | length=10, smooth_length=14, sensitivity=2.0 | Adaptive Trend Flow [QuantAlgo] (PUB;87158567b731451c8a1347f953921ab7). |
| `adx_sma` | extra | high, low, close | plus_di, minus_di, adx | length=14 | "ADX and DI" [BeikabuOyaji / MasaNakamura], used by ~40 FMZ strategies. |
| `adxr` | extra_hpotter | high, low, close | adxr, adx | length=14, hpotter=False | Wilder's ADXR = (ADX + ADX[length - 1]) / 2 on TradingView's ADX |
| `ahrens_ma` | extra_ma | close | ahma | length=9, seed='zero' | Ahrens Moving Average (Richard D. Ahrens, TASC Oct 2013): |
| `ama_channel` | extra_trend | close | ama, upper, lower, alpha | snr_factor=2.1, lookback=5, beta=2.1 | "[CS] AMA Strategy - Channel Break Out" (FMZ "Adaptive Moving Average |
| `ama_durenard` | extra_ma | close | ama, upper, lower | lookback=5, beta=2.1, snr_factor=2.1 | Adaptive MA channel from E. Durenard, "Professional Automated Trading" |
| `andean_oscillator` | extra_trend | open, close | bull, bear, signal | length=50, signal_length=9 | Andean Oscillator (alexgrover, 2022; alpaca.markets/learn article), |
| `atr_breakout_bands` | extra_trend | high, low, close | upper, lower, state | atr_length=120, mult=2.0 | ATR trend bands of the FMZ "Claw-Pattern" / ATR Trend Breakout |
| `atr_envelope` | extra_trend | source, high, low, close | upper, lower | length=34, mult=3.0 | ATR envelope of "baguette by multigrain" (credited to redktrader), |
| `atr_trailing_bands` | extra_trend | open, high, low, close | upper, lower, stop, pos | atr_length=5, mult=4.0, wick_length=30, wick_type='avg' | "ATR Trailing Stop Bands Strategy [R]" (River's mod of HPotter's port |
| `atr_trailing_support` | extra_trend | high, low, close | support | length=14 | Ratcheting ATR support (strategy-specific, ``ATR_func`` of the FMZ |
| `avellaneda_stoikov_quotes` | extra_trend | close | bid, ask, mid | gamma=2.0, sigma=8.0, t=0.0833, k=5.0, fee=0.0, model='tamim', inventory=0.0 | Bid / ask quotes. |
| `barssince` | extra | condition | bars |  | ``ta.barssince(cond)``; NaN before the first true bar. |
| `bill_williams_3lines` | extra_hpotter | high, low | jaw, teeth, lips | jaw_length=13, teeth_length=8, lips_length=5, jaw_offset=8, teeth_offset=5, lips_offset=3, hpotter=False | Bill Williams' three averages (the Alligator): SMMA of hl2, displaced |
| `binomial_ma` | extra_ma | close | bma | length=10 | Binomial Moving Average [HosseinDaftary]: weights C(2n-1, n-1-i) for |
| `blackflag_fts` | extra_misc | high, low, close | trail, trend, extremum, fib1, fib2, fib3 | trail_type='modified', atr_period=28, atr_factor=5.0 | Blackflag FTS (Jose Azcarate; v4 script by Duyck): ATR trailing stop |
| `bull_bear_balance` | extra_hpotter | open, high, low, close | bull, bear, balance | smooth=1 | Vadim Gimelfarb's Bull Power, Bear Power and Bull and Bear Balance |
| `candlestick_patterns` | extra_tv | open, high, low, close | on_neck_bear, rising_window_bull, falling_window_bear, falling_three_methods_bear, rising_three_methods_bull, tweezer_top_bear, tweezer_bottom_bull, dark_cloud_cover_bear, downside_tasuki_gap_bear, upside_tasuki_gap_bull, evening_doji_star_bear, doji_star_bear, doji_star_bull, morning_doji_star_bull, piercing_bull, hammer_bull, hanging_man_bear, shooting_star_bear, inverted_hammer_bull, morning_star_bull, evening_star_bear, marubozu_white_bull, marubozu_black_bear, doji, gravestone_doji_bear, dragonfly_doji_bull, harami_cross_bull, harami_cross_bear, harami_bull, harami_bear, long_lower_shadow_bull, long_upper_shadow_bear, spinning_top_white, spinning_top_black, three_white_soldiers_bull, three_black_crows_bear, engulfing_bull, engulfing_bear, abandoned_baby_bull, abandoned_baby_bear, tri_star_bull, tri_star_bear, kicking_bull, kicking_bear, inside_bar, pin_bar_bull, pin_bar_bear | trend_rule='SMA50', body_length=14, shadow_percent=5.0, shadow_equals_percent=100.0, doji_body_percent=5.0, factor=2.0, pin_ratio=0.6666666666666666 | TradingView's candlestick pattern built-ins, one bool output per pattern. |
| `chebyshev_filter` | extra_ma | close | filter | length=3.0, extra=True | ChartPrime Ichimoku Oscillator ``smoothing()``: ``chebyshevI(src, len, |
| `chebyshev_ma` | extra_ma | close | chebyshev | length=8.0, ripple=0.05 | "Chebyshev Type I Moving Average" of ChartPrime's Ichimoku Oscillator. |
| `cipher_b_rsimfi` | extra_misc | open, high, low, close | rsimfi | period=60, multiplier=150.0, pos_y=2.5 | VuManChu Cipher B "RSI+MFI Area" (``f_rsimfi``): |
| `cmo_average` | extra_hpotter | close | cmo_av | length1=5, length2=10, length3=20, absolute=False | CMOav: the average of Chande's CMO at three lengths (each 100 * |
| `cmo_disparity` | extra_hpotter | close | first, second, third | length1=50, length2=25, length3=10, hpotter=False | Disparity index on three EMAs, as in HPotter's "CMOaDisparity Index": |
| `cmo_filtered` | extra_hpotter | close | cmo | length=9, filter=3.0 | CMOfilt (Chande): CMO built only from bar changes larger than |
| `commodity_selection_index` | extra_hpotter | high, low, close | csi | length=14, point_value=50.0, margin=3000.0, commission=10.0, hpotter=False | Wilder's Commodity Selection Index ("New Concepts", 1978): |
| `comparative_relative_strength` | extra_hpotter | close, other | crs | length=10 | Comparative relative strength: SMA(close / other, length). |
| `conditional_ema` | extra_ma | close, condition | ema | length=20 | Conditional-sampling EMA (``Cond_EMA`` of DonovanWall's Range Filter |
| `confluence` | extra_hpotter | open, high, low, close | confluence | harmonic=10 | The "Confluence" indicator (TradeStation, ported by HPotter): it |
| `dapd_bands` | extra_hpotter | high, low | dapd, top, bottom | length=21 | DAPD (Daily Average Price Delta) bands: dapd = SMA(high) - SMA(low); |
| `deadband_double_sma` | extra_ma | close, deviation_source | mad | length=15, gamma=4.0, zero_lag=False | Double-SMA deadband average of the "Goblin Town" strategy |
| `deli` | extra_ehlers | close | dsp, deli, pos | length=7 | Detrended Ehlers Leading Indicator [HPotter] (after "MESA and Trading |
| `delta_rsi` | extra_misc | close | drsi, signal, nrmse | rsi_length=21, window=21, degree=2, signal_length=9 | Delta-RSI Oscillator [tbiktag]: time derivative of a local polynomial |
| `demark_reversal_points` | extra_trend | close | drp, signal, up_count, down_count | length=9, lb_length=4 | Demark Reversal Points [CC] (Franklin Moormann / cheatcountry). |
| `detrended_synthetic_price` | extra_hpotter | high, low | dsp | length=14 | Ehlers' Detrended Synthetic Price ("MESA and Trading Market Cycles"): |
| `dinapoli_detrended_oscillator` | extra_hpotter | close | osc | length=7 | Joe DiNapoli's Detrended Oscillator: close - SMA(close, 7) (no |
| `directional_trend_index` | extra_hpotter | high, low | dti | r_length=14, s_length=10, u_length=5 | Blau's Directional Trend Index: HMU = max(high - high[1], 0), LMD = |
| `divergence` | extra_tv | osc, high, low | bull, hidden_bull, bear, hidden_bear, pivot_low, pivot_high | lookback_left=5, lookback_right=5, range_upper=60, range_lower=5 | TradingView's "RSI divergence indicator" for any oscillator series. |
| `dma_cn` | extra | close, alpha | dma |  | MyLanguage DMA(X, A): exponential smoothing with a per-bar alpha series. |
| `doji` | extra_hpotter | open, close | doji | max_body=0.0 | Doji: body no larger than ``max_body`` (0 = open == close, which is |
| `dss_bressert` | extra_hpotter | high, low, close | dss, signal | length=10, smooth=9, signal_length=5 | Walter Bressert's Double Smoothed Stochastic: EMA of the raw %K, then |
| `dual_thrust` | extra_trend | open, high, low, close | buy_trigger, sell_trigger, buy_range, sell_range | length=4, k1=0.5, k2=0.5, sell_length=0 | Dual Thrust (Michael Chalek): Range = max(HH - LC, HC - LL) over the |
| `dynamic_momentum_index` | extra_hpotter | close | dmi, period | base_length=14, stdev_length=5, avg_length=10, min_length=5, max_length=30 | Chande & Kroll's Dynamic Momentum Index ("The New Technical Trader", |
| `dynamo` | extra_hpotter | high, low, close | dynamo, osc | osc_length=10, ma_length=20 | E. Marshall Wall's Dynamic Momentum Oscillator (Futures, Jul 1996) as |
| `edsma` | extra_ma | close | edsma | length=40, ssf_length=20, poles=2 | Ehlers Deviation-Scaled Moving Average [everget]. |
| `ehlers_agc` | extra_ehlers | close | normalized, peak | decay=0.991 | Ehlers automatic gain control, fast attack / slow decay (TASC Aug 2014, |
| `ehlers_bandpass` | extra_hpotter | high, low | bp | length=20, delta=0.5, hpotter=False | Ehlers' bandpass filter of hl2 (Ehlers & Way, TASC Mar 2010): |
| `ehlers_butterworth2` | extra_ehlers | close | butterworth | length=20, zero_seed=False | Ehlers 2-pole Butterworth low-pass ("Cybernetic Analysis", 2004): |
| `ehlers_butterworth3` | extra_ehlers | close | butterworth | length=20, method='ehlers' | 3-pole Butterworth low-pass, first three bars = price. |
| `ehlers_cosine_ifm` | extra_ehlers | close | period, inst_period | max_count=50 | Ehlers Cosine IFM dominant-cycle period ("Measuring Cycles", 1999): phase |
| `ehlers_cyber_cycle` | extra_ehlers | close | cycle, trigger, signal | alpha=0.07, signal_lag=9 | Ehlers Cyber Cycle ("Cybernetic Analysis", 2004, ch. 4): 2-pole high-pass |
| `ehlers_decycler` | extra_ehlers | close | decycler | length=60 | Ehlers Decycler ("Cycle Analytics for Traders", 2013, ch. 4): price minus |
| `ehlers_emd` | extra_ehlers | close | mean, upper, lower, trend, bp | length=20, delta=0.5, fraction=0.1, avg_length=50 | Ehlers & Way Empirical Mode Decomposition (TASC Mar 2010): trend |
| `ehlers_fisher_stoch` | extra_ehlers | close | fisher, trigger | length=10, normalize=False | Ehlers "Fisher Stochastic" of any series (Cybernetic Analysis, 2004: |
| `ehlers_highpass2` | extra_ehlers | close | hp | length=48 | Ehlers 2-pole high-pass filter (Cycle Analytics, 2013; roofing filter |
| `ehlers_hilbert_period` | extra_ehlers | close | period, inst_period | max_count=50 | Ehlers' original phase-accumulation cycle measurer (the "original |
| `ehlers_homodyne_dc` | extra_ehlers | close | period, smooth_period |  | Ehlers Hilbert-transform homodyne dominant cycle ("Rocket Science for |
| `ehlers_iq_ifm` | extra_ehlers | close | period, inst_period | max_count=50, seed=0.0 | Ehlers I-Q IFM dominant-cycle period ("Measuring Cycles", 1999, SideBar 1): |
| `ehlers_leading_indicator` | extra_hpotter | high, low | eli, dsp | length=7 | Ehlers Leading Indicator as in the D_ELI scripts: DSP - EMA(DSP, L). |
| `ehlers_optimal_tracking` | extra_ehlers | source, high, low, close | otf | true_range=False | Ehlers Optimal Tracking Filter (Kalata tracking index): lambda = |
| `ehlers_reflex` | extra_ehlers | close | reflex | length=20, ss_length=0, ms_alpha=0.04 | Ehlers Reflex (TASC Feb 2020): like Trendflex but each difference is |
| `ehlers_roofing_filter` | extra_ehlers | close | roofing | hp_length=48, ss_length=10 | Ehlers Roofing Filter (Cycle Analytics / TASC Jan 2014): 2-pole high-pass |
| `ehlers_smoothed_rsi` | extra_hpotter | close | rsi | length=10 | Ehlers' Smoothed RSI ("Cybernetic Analysis", 2004): RSI (0..1) of the |
| `ehlers_super_passband` | extra_ehlers | close | pb, rms | fast_length=40, slow_length=60, rms_length=50 | Ehlers Super Passband filter (TASC Jul 2016): difference of two |
| `ehlers_trendflex` | extra_ehlers | close | trendflex | length=20, ss_length=0, ms_alpha=0.04 | Ehlers Trendflex (TASC Feb 2020, "Reflex: A New Zero-Lag Indicator"): |
| `ehlers_voss` | extra_ehlers | close | voss, filt | period=20, predict=3, bandwidth=0.25 | Ehlers Voss predictive filter (TASC Aug 2019, "A Peek Into The Future"): |
| `ehlers_zero_lag_ec` | extra_ehlers | close | ec, ema, least_error, best_gain | length=20, gain_limit=50 | Ehlers & Way Zero Lag (error-correcting) EMA, TASC Nov 2010 "Zero Lag |
| `ehlers_zero_lag_ec_adaptive` | extra_ehlers | close, period | ec, ema, least_error, best_gain | gain_limit=50 | Zero Lag EC with a per-bar period series (alpha = 2/(period+1)), as in |
| `ema_volume_weighted` | extra_hpotter | close, volume | ema_vw | length=22 | Exponential volume-weighted average: ema(volume * close) / ema(volume) |
| `empirical_mode_decomposition` | extra_hpotter | high, low | mean, peak, valley | length=20, delta=0.5, fraction=0.1, avg_length=50, hpotter=False | Ehlers & Way's Empirical Mode Decomposition (TASC Mar 2010): mean = |
| `engulfing` | extra_hpotter | open, close | bull, bear | min_body=0.0 | Engulfing patterns as in HPotter's Bearish Engulfing backtest (the |
| `ergodic_candlestick_oscillator` | extra_hpotter | open, high, low, close | csi, signal | r_length=32, s_length=12, u_length=1, q_length=1, signal_length=5 | Blau's Candlestick Index CSI(q, r, s, u) and its Ergodic signal: |
| `ergodic_mdi` | extra_hpotter | close | mdi, signal | r_length=32, s_length=5, u_length=5, signal_length=5 | Blau's Ergodic Mean Deviation Indicator: MDI = E_u(E_s(close - |
| `ergodic_tsi` | extra_hpotter | close | tsi, signal | r_length=25, s_length=13, u_length=1, signal_length=5 | Blau's True Strength Index TSI(r, s, u) = |
| `essma` | extra_ma | source, open, close | essma | length=50, w1=2.0, w2=2.0, w3=2.0, w4=2.0, w5=2.0 | ESSMA [bhavishya] (strategy-specific): |
| `evwma` | extra_ma | close, volume | evwma | length=20, seed='close', cumulative=False | Elastic Volume Weighted Moving Average (Christian P. Fries, 2001). |
| `extracting_the_trend` | extra_hpotter | high, low | trend, bp | length=20, delta=0.5, hpotter=False | Ehlers & Way's trend extraction (TASC Mar 2010): the 2*L-bar SMA of |
| `fair_value_gap` | extra | high, low | bull, bear, bull_top, bull_bottom, bear_top, bear_bottom |  | Fair Value Gaps (ICT / SMC), known on the bar that completes them. |
| `fast_slow_kurtosis` | extra_hpotter | close | kurtosis, fast, fast_slow | length=65, wma_length=3 | Fast & Slow Kurtosis (MetaStock "Kurtosis"): K = mom(mom(close, 3), 1), |
| `faytterro_estimator` | extra_misc | close | estimator, forecast, buy, sell | length=10 | Faytterro Estimator strategy core [faytterro] (strategy-specific). |
| `fib_levels` | extra | high, low | l0, l236, l382, l500, l618, l786, l100 | length=100 | Fibonacci retracement levels of the rolling ``length``-bar range, |
| `fib_progression_breaks` | extra_trend | high, low, close | avg, dist, os, buy, sell, target, stop, fib_n | method='atr', size=1.0, sequence_length=3 | Fibonacci Progression With Breaks [LuxAlgo] (PUB;91fffae7...). |
| `finite_volume_elements` | extra_hpotter | high, low, close, volume | fve | period=22, factor=0.3, hpotter=False | Markos Katsanos' Finite Volume Elements (TASC Apr 2003). |
| `fisher_transform` | extra_hpotter | high, low | fisher, trigger | length=10, hpotter=False | Ehlers' Fisher Transform of hl2 ("Cybernetic Analysis", 2004): the |
| `for_loop_score` | extra_misc | close | score | start=1, end=50 | "For-loop" trend score: +1 for every lag i in start..end where the |
| `fractal_chaos_bands` | extra_hpotter | high, low | upper, lower | pattern=1 | Fractal Chaos Bands (Edward Dobson's band form of Bill Williams' |
| `fractal_chaos_oscillator` | extra_hpotter | high, low | fco | pattern=1 | Fractal Chaos Oscillator: +1 on the bar a new up-fractal level appears, |
| `ftsma` | extra_ma | close | ftsma | harmonic=1, ma_length=20, lookback=64, ma_type='ema' | FTSMA [03.freeman] on xyse's Low-Frequency Fourier Transform. |
| `g_channel` | extra_trend | close | upper, lower, avg, bullish | length=100, seed='zero' | G-Channels [alexgrover] with the trend rule of "G-Channel Trend |
| `gann_swing_oscillator` | extra_hpotter | high, low | gso | length=5 | Gann Swing Oscillator (Robert Krausz, "A W.D. Gann Treasure |
| `gaussian_channel` | extra | high, low, close | filter, upper, lower | period=144, poles=4, mult=1.414, reduced_lag=False, fast_response=False | Gaussian Channel [DonovanWall]: Gaussian filter of hlc3, bands from the |
| `gaussian_filter` | extra | close | gaussian | period=14, poles=4 | Ehlers Gaussian filter with 1-9 poles (zero-seeded, as the Pine ports). |
| `gaussian_fir` | extra_ma | close | mid, std | length=20 | Gaussian-weighted window average and stdev (strategy-specific |
| `gaussian_stdev_channel` | extra_misc | close | mid, stdev, upper, lower | length=20, mult=2.0 | Gaussian-weighted mean and standard deviation over the last ``length`` |
| `geometric_mean_ma` | extra_ma | close | gmean | length=20 | Rolling geometric mean, prod(src[i]^(1/n)) (MA Emperor's |
| `gyroscopic_bands` | extra_misc | close | pos, upper, lower, traj | a_exp=4.0, b=12 | Jomy's Gyroscopic Bands (strategy-specific). |
| `harami` | extra_hpotter | open, close | bull, bear | min_body=0.0 | Bullish / bearish harami as in HPotter's Harami backtests: the current |
| `henderson_ma` | extra_ma | close | hwma | length=7 | Henderson Weighted Moving Average [everget]: the (2m+1)-term Henderson |
| `high_low_bands` | extra_hpotter | close | basis, upper, lower | length=14, percent=1.0, hpotter=False | High Low Bands: a triangular MA shifted up and down by ``percent``. |
| `hl_range_histogram` | extra_hpotter | high, low, close | value, average | length=13, percent=False | (H-L)/C histogram: high - low (or 100 * (high - low) / close when |
| `hpotter_center_of_gravity` | extra_hpotter | close | cog, upper1, lower1, upper2, lower2 | length=20, offset=5, percent=1.0 | HPotter's "Center of Gravity" bands: linreg(close, length, offset) |
| `hpotter_money_flow` | extra_hpotter | open, high, low, close, volume | mf | fast=3, slow=10 | HPotter's "Money Flow Indicator (Chaikin Oscillator)": with |
| `hpotter_obos` | extra_hpotter | high, low, close | obos | length=10 | HPotter's Overbought/Oversold: stoch(length) / 100 when close > |
| `hpotter_three_line_break` | extra_hpotter | close | trend, line, line3 |  | HPotter's "modified" Three Line Break: a close-only state machine on |
| `hurst_exponent` | extra_misc | close | hurst | length=50 | Hurst exponent from the rescaled range of the last ``length`` log |
| `hv_lv` | extra | high, low | hv, lv | length=20 | Highest high / lowest low of the previous ``length`` bars, excluding the |
| `hysteresis_filter` | extra_ma | close | lazy | laziness=0.04 | "Lazy" hysteresis line (``lz()`` of the "Adaptive Grid" strategy, |
| `inertia` | extra_hpotter | high, low, close | inertia | stdev_length=10, smooth=14, linreg_length=20, ema_length=14, hpotter=False | Dorsey's Inertia (TASC Sep 1995, "Refining the Relative Volatility |
| `jma` | extra | close | jma | length=7, phase=50, power=2 | Jurik Moving Average, the open approximation in [everget]'s TV script |
| `jurik_rsx` | extra_ma | close | rsx | length=14 | Jurik RSX, the public port of Jurik's noise-free RSI (everget's / |
| `kalman_alpha_beta` | extra_ma | close | kalman, velocity | gain=0.7, scale=1.0, sharpness=2.0 | The TradingView community "Kalman" filter (Hull Suite / BRAHMASTRA |
| `kama` | extra_hpotter | close | kama | length=10, fast=2, slow=30, hpotter=False | Kaufman's Adaptive Moving Average (same numbers as |
| `kase_dev_stops` | extra_hpotter | high, low, close | warning, dev1, dev2, dev3, direction | length=30, dev_length=30, mult1=1.0, mult2=2.2, mult3=3.6, hpotter=False | Cynthia Kase's Dev-Stops ("Trading with the Odds"; "Kase Dev Stop", |
| `kdj` | extra | high, low, close | k, d, j | length=9, k_smoothing=3, d_smoothing=3 | KDJ, the Chinese stochastic (FMZ ``TA.KDJ``, Tongdaxin, Wenhua). |
| `keltner_original` | extra_hpotter | high, low, close | basis, upper, lower | length=10, mult=1.0 | Chester Keltner's original channel ("How to Make Money in |
| `kernel_ma` | extra_ma | close | kma | length=20, kernel='beta', alpha=3.0, beta=3.0, bandwidth=0.3 | Kernel-weighted MA of the "B4100 NW Trend Ribbon" strategy |
| `kernel_regression_chartprime` | extra_ma | close | kernel | size=64, h=4.0, r=0.5 | ``gaussian_kernel(source, size, h, r)`` of ChartPrime's Ichimoku |
| `key_reversal` | extra_hpotter | high, low, close | up, down | length=1 | Key reversal bars: ``up`` = low below the lowest low of the previous |
| `klinger_volume_oscillator` | extra_hpotter | high, low, close, volume | kvo, signal | fast=34, slow=55, signal=13, hpotter=False | Stephen Klinger's Volume Oscillator with his Volume Force |
| `knn_mean` | extra_ma | value, target | knn | k_neighbors=3, window=30 | Mean of the ``k_neighbors`` values among value[1..window] closest to |
| `kwan_nrp` | extra_hpotter | open, high, low, close | knrp | momentum_length=9, rsi_length=9, stoch_length=9, nrp_length=2 | Kwan NRP as ported by HPotter: the ``nrp_length``-bar average of |
| `leledc_exhaustion` | extra_trend | open, high, low, close | major, minor | major_qual=6, major_len=30, minor_qual=5, minor_len=5, close_lookback=4, index_lookback=1 | Leledc Exhaustion Bar (glaz's Pine v2 original, as ported by Joy_Bangla, |
| `linreg_channel` | extra_tv | high, low, close | upper, mid, lower, pearson_r, slope, stdev | length=100, upper_mult=2.0, lower_mult=2.0, use_upper_dev=True, use_lower_dev=True | TradingView's "Linear regression channel" (``STD;Linear_Regression``), |
| `logistic_price_forecast` | extra_trend | close, volume | forecast, z | std_length=20, z_std_length=100, z_sma_length=10 | The FMZ "Logistic" strategy's forecast, strategy-specific. |
| `ma_angle_atr` | extra_ma | source, high, low, close | angle | lookback=1, atr_length=14, per_bar=False | Slope angle in degrees: ``atan((src - src[lookback]) / atr) * 180/pi``. |
| `ma_converging` | extra_ma | high, low, close | ma, fma | length=100, incr=10, fast=10 | MA Converging [LuxAlgo] (the "Dual MA Momentum Breakout" strategy). |
| `ma_displaced_envelope` | extra_hpotter | close | upper, lower, basis | length=9, percent_above=0.5, percent_below=0.5, displacement=13 | Moving Average Displaced Envelope: EMA(length) taken ``displacement`` |
| `mama` | extra | close | mama, fama | fast_limit=0.5, slow_limit=0.05 | Ehlers MESA Adaptive Moving Average (MAMA/FAMA), from Ehlers' |
| `modified_pvt` | extra_hpotter | open, high, low, close, volume | mpvt, signal | level=1.0, scale=1.0, length=23, volume_divisor=50000.0 | Modified Price-Volume Trend (HPotter, after the TASC article): the PVT |
| `moonflag_average` | extra_ma | close | mfa | gaps=12 | MoonFlagAverage [MoonFlag] (strategy-specific): d(d(d(x))) where |
| `most` | extra_trend | close | most, mavg, direction | length=3, percent=2.0, ma_type='ema', method='kivanc' | MOST, Moving Stop Loss (Anil Ozeksi; KivancOzbilgic's TradingView code). |
| `multi_kernel_regression` | extra_ma | close | mkr, gaussian, epanechnikov | length=30, h_gaussian=5.0, h_epanechnikov=5.0, gaussian_weight=0.5 | One-sided (no look-ahead) Nadaraya-Watson kernel regression of the |
| `n_bars_up_down` | extra_hpotter | open, close | up_count, down_count | hpotter=False | Run length of consecutive up bars (close >= open) and down bars |
| `nadaraya_watson_rq` | extra_misc | close | yhat1, yhat2 | h=8.0, r=8.0, x_0=25, lag=2, size=1 | Nadaraya-Watson: Rational Quadratic Kernel (Non-Repainting) [jdehorty]. |
| `nma_durschner` | extra_ma | close | nma | length=20, length2=0, ma_type='wma' | Moving Average 3.0 (M. G. Duerschner, "Gleitende Durchschnitte 3.0", |
| `obv_macd_ma` | extra_ma | close | ma | length=9, ma_type='DEMA', nma_length2=26 | The ``myma()`` selector of OBV MACD [RafaelZioni] (also Smooth HA |
| `ols_regression` | extra_trend | y, x | intercept, slope | length=21 | Rolling least squares y = a + b*x over ``length`` bars (both |
| `p_signal` | extra_misc | close | psignal, raw | points=9, version=4 | P-Signal [Kharevsky]: ``sma(fPSignal(change(src), n), n)``, n = points-1. |
| `percentile` | extra | close | percentile | length=20, percentage=50.0, method='linear' | ``ta.percentile_linear_interpolation`` (method="linear") or |
| `period_high_low` | extra_hpotter | high, low, session | high, low | lookback=1 | High and low of the calendar period ``lookback`` periods ago, i.e. |
| `pivot_atr` | extra_trend | high, low, close | pivot_high, pivot_low | left=4, right=2, atr_length=14, atr_mult=0.1 | Significant pivots of "Pivot of Pivot Reversal Strategy [QuantNomad]" |
| `pivot_detector_oscillator` | extra_hpotter | close | pdo | ma_length=200, rsi_length=14, up_entry=35.0, up_exit=85.0, down_entry=20.0, down_exit=70.0 | Siligardos' Pivot Detector Oscillator (TASC Jul 2009): RSI(14) |
| `pivot_point_supertrend` | extra_trend | high, low, close | supertrend, trend, center, up, down, support, resistance, buy, sell | period=2, factor=3.0, atr_period=10 | Pivot Point SuperTrend [LonesomeTheBlue] (PUB;HN4w1eNW3B9HP5oSa2MNMIHMYUqLPHUT). |
| `pivothigh` | extra_tv | high | pivot, found | leftbars=10, rightbars=10, strict=False | ``ta.pivothigh(src, leftbars, rightbars)``, reported on the confirmation bar. |
| `pivotlow` | extra_tv | low | pivot, found | leftbars=10, rightbars=10, strict=False | ``ta.pivotlow(src, leftbars, rightbars)``, reported on the confirmation bar. |
| `pmax` | extra_trend | high, low, close | pmax, mavg, direction, buy, sell | atr_length=10, multiplier=3.0, ma_type='ema', ma_length=10, change_atr=True, normalize=False, source='hl2' | Profit Maximizer (PMax) [KivancOzbilgic] (PUB;ps6kWkOWqLJPZhvTAj2ORDYjN1ewE9gA). |
| `pmax_core` | extra_trend | mavg, atr | pmax, direction | multiplier=3.0 | PMax line from a precomputed average and ATR (``Pmax_Func`` of the FMZ |
| `polarized_fractal_efficiency` | extra_hpotter | close | pfe, raw | length=10, smooth=5, hpotter=False | Hans Hannula's Polarized Fractal Efficiency (TASC Jan 1994): |
| `price_friction` | extra_misc | high, low, close | friction, low_f, high_f, mid_f, trigger | barsback=500, range_length=100, flevel=50.0, tlevel=-10.0 | "LUBE" price friction (strategy-specific). |
| `prime_number_bands` | extra_hpotter | high, low | upper, lower | percent=5.0, scale=1.0, hpotter=False | Prime Number Bands: nearest prime at or above the high (upper) and at |
| `prime_number_oscillator` | extra_hpotter | close | pno | percent=5.0, scale=1.0, hpotter=False | Prime Number Oscillator: distance from the price to the nearest prime |
| `pring_special_k` | extra_hpotter | close | special_k, signal | smooth=10 | Martin Pring's Special K (daily): the sum of 12 smoothed ROCs |
| `quadratic_wma` | extra_ma | close | qwma | length=20 | WMA with weights (n - i)^2 (strategy-specific ``wma()`` of the "MACD and |
| `rainbow_oscillator` | extra_hpotter | close | rbo, bandwidth | length=2, levels=10, hhll_length=10 | Mel Widner's Rainbow Oscillator (TASC 1997): ``levels`` recursive |
| `range_filter_dw` | extra_trend | high, low, close | filter, high_band, low_band, direction | filter_type=1, movement_source='close', range_size=2.618, range_scale='average change', range_period=14, smooth_range=True, smooth_period=27, average_filter=False, average_samples=2, mintick=0.01, pointvalue=1.0 | Range Filter [DW] (DonovanWall, v4 array version, |
| `range_filter_trailing` | extra_trend | close | filter, upper, lower, trail | fast_period=27, fast_range=1.6, slow_period=55, slow_range=2.0 | Twin Range Filter [colinmck] with the SuperTrend-style trailing band |
| `range_volatility` | extra_misc | close | volatility, upper, lower, mid | length=100, avg_length=100 | Volatility Range Breakout [wbburgin] (strategy-specific). |
| `ratio_ochl_averager` | extra_ma | open, close, range_high, range_low | rochla | recursive=False | Ratio OCHL Averager [alexgrover]: an EMA whose alpha is the candle body |
| `ravi` | extra_hpotter | close | ravi | fast=7, slow=65, hpotter=False | Chande's Range Action Verification Index ("Beyond Technical Analysis"): |
| `recursive_bands` | extra_trend | high, low, close | upper, lower, middle | length=100, method='classic' | (Extended) Recursive Bands [alexgrover] (PUB;qLuJ87gK9HlpqlLanJfXD0KcwwZejDzz). |
| `recursive_moving_trend_average` | extra_hpotter | close | rmta | length=21 | Dennis Meyers' Recursive Moving Trend Average (TASC Dec 1998, "The |
| `redk_vader` | extra_misc | high, low, close, volume | demand, supply, vader, signal, sentiment | length=10, der_avg=5, ma_type='WMA', smooth=3, senti=20, v_calc='Relative', vlookbk=20 | RedK Dual VADER with Energy Bars (VADER v4.0, same core as v3.0) [RedKTrader]. |
| `relative_body_index` | extra_misc | open, high, low, close | rbi, signal | length=5, signal_length=5, binary=False | Relative Body Index [Vitelot] (strategy-specific): ema(sum(rb, n), n) |
| `rema` | extra_ma | close | rema | length=10, lam=0.5, seed='zero' | Regularized EMA (Chris Satchwell, TASC 2003): |
| `renko` | extra_trend | high, low, close | brick_open, brick_close, direction, new_bricks | method='atr', box_size=1.0, atr_length=14, percent=1.0 | Renko bricks built from closes, as known at each bar's close. |
| `retro_wma` | extra_ma | close | rwma | length=20 | "Retro weighted MA" (strategy-specific, RSI Trend Following |
| `reversal_123` | extra | high, low, close | pos, k, d | length=14, k_smoothing=1, d_length=3, level=50 | 123 Reversal [HPotter] (Ulf Jensen, "Street Smarts"), used by 128 FMZ |
| `reverse_engineering_rsi` | extra_hpotter | close | price | rsi_value=50.0, wilder_length=14, hpotter=False | Giorgos Siligardos' Reverse Engineering RSI (TASC Jun 2003): the close |
| `rising_falling` | extra | close | rising, falling | length=3 | ``ta.rising`` / ``ta.falling``: strictly higher (lower) than each of |
| `rsi_divergence` | extra_tv | close, high, low | bull, hidden_bull, bear, hidden_bear, pivot_low, pivot_high | length=14, lookback_left=5, lookback_right=5, range_upper=60, range_lower=5 | The built-in exactly: ``divergence(ta.rsi(close, 14), high, low)``. |
| `rsi_heikin_ashi` | extra_misc | high, low, close | open, high, low, close | length=14, smoothing=1 | Heikin Ashi RSI Oscillator [JayRogers] (``f_rsiHeikinAshi``). |
| `rsi_trend_threshold` | extra_trend | source, high, low, close | threshold, direction | length=8, mult=1.5, min_diff=10.0 | ``rsilev`` of the FMZ "RSI Trend Reversal" strategy, strategy-specific. |
| `rvi_dorsey` | extra_hpotter | close | rvi | stdev_length=10, smooth=14, hpotter=False | Donald Dorsey's Relative Volatility Index (TASC Jun 1993): RSI built |
| `rwma_range` | extra_ma | high, low, close | rwma | length=20 | Range-weighted MA of TZack88's RMI Trend Sniper (``calculateRwma``): |
| `session_vwma` | extra_ma | close, volume, session | vwma | length=55, include_session_open=True | VWMA whose length is capped at the bars elapsed in the current session |
| `signal_to_noise` | extra_hpotter | close | stn | length=21 | HPotter's "Signal To Noise": -10 * ln(sum over i = 1..length-1 of |
| `signed_wma` | extra_ma | source, open, close | swma | length=5 | Linear WMA whose terms are negated on down candles (close < open): |
| `sine_fir_filter` | extra_ma | close | filter | length=50, alpha=1.0, beta=0.5 | FIR filter with kernel sin(2*pi*x^alpha)*(1 - x^beta), x = i/(n-1), |
| `sine_wma` | extra_ma | close | swma | length=14, insilico_compat=False | Sine-Weighted Moving Average [everget]: weight sin((i+1)*pi/(n+1)) for |
| `sizeblock` | extra_trend | open, high, low, close | mid, upper, lower | deviation=1.0, u_turn=2.0, dev_type='percentage', source='close', mintick=0.0 | Sizeblock (strategy-specific, FMZ "趋势成块策略Sizeblock-Strategy", |
| `slope_adaptive_ma` | extra_ma | high, low, close | sama | length=200, min_length=6, maj_length=14 | Slope Adaptive Moving Average [MightyZinger] (MZ SAMA ``ama()``). |
| `sma_cn` | extra | close | sma_cn | length=3, weight=1 | Chinese SMA(X,N,M) (MyLanguage/Tongdaxin): Y = (M*X + (N-M)*Y')/N. |
| `smart_money_index` | extra_hpotter | open, close, session | smi | first_bars=1, last_bars=1, start=0.0 | Don Hays' Smart Money Index on intraday bars: |
| `smart_money_index_hpotter` | extra_hpotter | open, close, htf_open, htf_close | smi |  | HPotter's Smart Money Index, for reproducing his strategies: |
| `ssf2` | extra | close | ssf | length=10 | Ehlers 2-pole Super Smoother, "Cycle Analytics" form (``get2PoleSSF``). |
| `ssf3` | extra | close | ssf | length=10 | Ehlers 3-pole Super Smoother (``get3PoleSSF``). |
| `ssl_hybrid_ma` | extra_ma | close, high, low | ma | length=60, ma_type='HMA', kidiv=1, jurik_phase=3, jurik_power=1, volatility_lookback=10, mf_beta=0.8, mf_feedback=False, mf_z=0.5, ssf_length=20, ssf_poles=2 | The ``ma(type, src, len)`` selector of SSL Hybrid [Mihkel00]. |
| `standard_error_bands` | extra_trend | close | middle, upper, lower, see | length=21, mult=2.0, smoothing=3 | Standard Error Bands (Jon Andersen, TASC Sept 1996). |
| `statistical_volatility` | extra_hpotter | high, low, close | sv | length=30, annual=253 | Statistical volatility by the extreme-value method (Parkinson's |
| `stdev_sample` | extra | close | stdev | length=20 | Sample standard deviation (divide by n-1): MyLanguage ``STD``, |
| `step_line` | extra_ma | close, band | step |  | Deadband step line: follows the source only when it moves more than |
| `superichi` | extra_trend | high, low, close | tenkan, kijun, senkou_a, senkou_b, cloud_a, cloud_b | tenkan_len=9, tenkan_mult=2.0, kijun_len=26, kijun_mult=4.0, spanb_len=52, spanb_mult=6.0, offset=26 | SuperIchi [LuxAlgo] (PUB;ec52552d888e467b9e25df03bad61c85): Ichimoku |
| `t3_cci` | extra_hpotter | close | t3cci, cci | cci_length=14, t3_length=5, b=0.618 | FX Sniper's T3-CCI (MT4), ported by HPotter: a Tillson T3 of |
| `tchannels` | extra_ma | close | line, band, trend | mult=1.0 | T-Channels [alexgrover] step line, as reused in OBV MACD |
| `td_sequential` | extra_trend | high, low, close | buy_count, sell_count, buy_setup, sell_setup, buy_setup_complete, sell_setup_complete, buy_perfected, sell_perfected, buy_countdown, sell_countdown, buy_13, sell_13, tdst_resistance, tdst_support | lookback=4, setup_length=9, countdown_length=13, countdown_lookback=2 | Tom DeMark's TD Setup and TD Sequential (rules as in Jason Perl, |
| `tfs_volume_oscillator` | extra_hpotter | open, close, volume | vo | length=7 | TFS Volume Oscillator (Strain & Whitley's TFS system, 2nd component): |
| `three_bar_reversal` | extra_hpotter | open, high, low, close | bull, bear |  | 3-Bar Reversal Pattern (HPotter): ``bull`` = bearish bar two bars ago, |
| `three_inside` | extra_hpotter | open, close | up, down |  | Three Inside Up / Down (a harami confirmed by a third bar that closes |
| `three_ten_oscillator` | extra_hpotter | high, low, close | osc, signal | fast=3, slow=10, signal=16, hpotter=False | Linda Raschke's 3/10 oscillator ("Street Smarts"): SMA3 - SMA10 of |
| `tillson_gd` | extra_ma | close | gd | length=5, vfactor=0.7 | Tillson's Generalized DEMA, the T3 building block: |
| `tmo` | extra_misc | open, close | main, signal, raw | length=14, calc_length=5, smooth_length=3, start=0 | True Momentum Oscillator (Mobius, thinkorswim 2018). |
| `trailing_stop_flip` | extra_trend | high, low, close | stop | long_offset=228.5, short_offset=243.5 | "BitMex Trailing Stop Strategy" by River (FMZ "Dynamic Trailing Stop"), |
| `trama` | extra_ma | high, low, close | trama | length=99 | Trend Regularity Adaptive Moving Average [LuxAlgo]. |
| `trend_analysis_index` | extra_hpotter | close | tai | avg_length=28, tai_length=5 | Trend Analysis Index: 100 * (HHV - LLV of SMA(close, 28) over 5 bars) |
| `trend_continuation_factor` | extra_hpotter | close | plus_tcf, minus_tcf | length=35 | M.H. Pee's Trend Continuation Factor (TASC Mar 2002). |
| `trend_intensity_index` | extra_hpotter | close | tii | major_length=60, minor_length=30 | M.H. Pee's Trend Intensity Index (TASC Jun 2002): over the last |
| `trend_persistence` | extra_trend | close, length | trend_persistence | smoothing=3 | ``trendPersistence`` of the FMZ "VAWSI and Trend Persistence Reversal" |
| `trend_score` | extra_trend | close | score | from_index=11, to_index=20 | Tushar Chande's TrendScore ("Rating Trend Strength", TASC Sept 1993): |
| `trend_thrust_indicator` | extra_trend | close, volume | tti, signal | fast=13, slow=26, signal=9 | Trend Thrust Indicator (Buff Pelz Dormeier, TASC Aug 2011; PineCodersTASC |
| `trend_trader` | extra_trend | high, low, close | trend_line, pos | length=21, multiplier=3.0 | Andrew Abraham's Trend Trader ("Trading the Trend", TASC Sept 1998), |
| `tsf` | extra | close | tsf | length=14 | Time Series Forecast: the regression line projected one bar ahead. |
| `tstep_lsma` | extra_ma | close | tstep, step, trend | length=100, sc=0.5 | T-Step LSMA [alexgrover]: a step line b on a recursively smoothed |
| `ttm_scalper` | extra_hpotter | high, low, close | level, state |  | TTM Scalper (John Carter, "Mastering the Trade") as approximated in |
| `uhl_ma` | extra_ma | close | cma, cts | length=100, mult=1.0 | Andreas Uhl's corrected moving average and alexgrover's "Uhl MA |
| `valuewhen` | extra | condition, close | value | occurrence=0 | ``ta.valuewhen(cond, src, occurrence)``. |
| `vawma` | extra_ma | close, high, low, volume | vawma | length=20 | Volume- and ATR-weighted MA from the VAWSI strategy (strategy-specific). |
| `vawsi` | extra_misc | src, high, low, close, volume | vawsi | length=14 | VAWSI: RSI whose gains/losses are averaged with ``vawma``, a weighted |
| `vawsi_hln` | extra_misc | src, high, low | hln | length=14 | ``hln`` from the same VAWSI strategy (strategy-specific): the absolute |
| `vertical_horizontal_filter` | extra_hpotter | high, low, close | vhf | length=28, hpotter=False | Adam White's Vertical Horizontal Filter: (HHV(close) - LLV(close)) / |
| `vma_lazybear` | extra_ma | close | vma | length=6, seed='zero' | Variable Moving Average [LazyBear] (Chande's VIDYA idea driven by a |
| `volatility_fve` | extra_hpotter | high, low, close, volume | fve, signal, cutoff | samples=22, perma=40, cintra=0.1, cinter=0.1, hpotter=False | Katsanos' volatility-adjusted FVE (TASC Sep 2003). |
| `volumatic_vidya` | extra_trend | high, low, close | vidya, upper, lower, trend_up, trail | length=10, momentum=20, band_distance=2.0 | Volumatic Variable Index Dynamic Average [BigBeluga] (PUB;04a9de6f...), |
| `volume_heatmap` | extra_misc | open, high, low, close, volume | buy, sell | lookback=100, levels=10, range_pct=0.01 | "Buy and Sell Volume Heatmap" totals (strategy-specific). |
| `volume_index` | extra_hpotter | close, volume | index, signal | negative=False, signal_length=255, roc_length=1, start=1000.0, hpotter=False | Fosback's Positive (``negative=False``) / Negative Volume Index. |
| `volume_profile` | extra_misc | high, low, volume | poc, vah, val | length=100, rows=24, value_area=70.0 | Rolling volume profile of the last ``length`` bars (current bar |
| `volume_rsi` | extra_misc | close, volume | rsi | length=14 | Volume RSI (``RSI_Volume`` / ``calc_rsi_volume``): RSI of |
| `volume_strength` | extra_misc | high, low, close, volume, session | sspv, ssnv, pos, neg |  | Volume Strength Finder [Saravanan_Ragavan] (strategy-specific). |
| `vpci` | extra_misc | close, volume | vpci | short=5, long=20 | Volume Price Confirmation Indicator (Buff Dormeier, TASC July 2007). |
| `vw_deviation_bands` | extra_misc | close, volume | basis, dev, upper2, upper3, lower2, lower3 | length=60, kind='average', log_space=False | BabyShark VWAP bands [GreatestUsername]: rolling volume-weighted mean of |
| `vwema` | extra_ma | close, volume | vwema | length=20 | Exponential volume-weighted MA: ``ema(src*volume, n) / ema(volume, n)`` |
| `wami` | extra_hpotter | close | wami | wma_length=4, ema_length=13 | WAMI: EMA(EMA(WMA(mom(close, 1), 4), 13), 13), as in HPotter's port. |
| `weighted_stdev` | extra_misc | close, weight | mean, variance, dev, mse, rmse | length=20 | Weighted mean / standard deviation over the last ``length`` bars |
| `weighted_stdev_linear` | extra_misc | close | mean, variance, dev, mse, rmse | length=20 | ``f_weighted_sd_from_arrays`` as used in the same script: linear weights |
| `weis_wave_volume` | extra_misc | close, volume | wave, wave_volume, up, down | length=2, below_zero=True | Weis Wave Volume [LazyBear]: volume accumulated over each wave. |
| `wilder_volatility_trail` | extra_trend | high, low, close | stop, upper_trail, lower_trail | atr_mult=3.0, atr_length=7, atr_ma='rma', sic_type='close' | "Wilder's Volatility Trailing Stop Strategy with various MA's" |
| `windowed_ema` | extra_ma | close | wema | length=20, decay=nan | EMA weights truncated to ``length`` bars and renormalised: |
| `wwma` | extra | close | wwma | length=14 | Welles Wilder MA as coded in Kivanc's scripts (``Wwma_Func``). |
| `zigzag` | extra_tv | high, low | direction, pivot_price, pivot_bar, prev_price, prev_bar, new_pivot, updated, swing_high, swing_high_bar, swing_low, swing_low_bar | deviation=5.0, depth=10, allow_zigzag_on_one_bar=True | TradingView's "Zigzag" (``STD;Zig_Zag``, library TradingView/ZigZag/9), |
| `zlema_half_lag` | extra | close | zlema | length=20 | ZLEMA with lag = floor(length/2), as in Kivanc's ``Zlema_Func``. |
| `zvwap` | extra_misc | close, volume | zvwap | length=20 | Z distance from VWAP [LazyBear]: (close - mean) / sqrt(sma((close - mean)^2, n)), |
