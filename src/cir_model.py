
def simulate_cir_trajectories(kappa, theta, sigma, r0, T_years, N, M, seed=123):
    """
    This function calculates the rates trajectories under a CIR model, which incorporates a mean reversion aspect and a long term rate view.

    This option allows us to set a mean and a long term view that might incorporate rates decreasing.

    params:

    kappa:
    theta:
    sigma: Annualized volatility
    r0: Starting rate
    T_years: Time in years
    N_steps: Ammount of working days
    M: Ammount of simulations
    Returns:
    - rates: Array of shape (N+1, M) with interest rate paths
    """


    dt = T_years / N
    np.random.seed(seed)
    rates_CIR = np.zeros((N + 1, M))
    rates_CIR[0, :] = r0

    for m in range(M):
        for t in range(1, N + 1):
            r_t = rates_CIR[t - 1, m]
            dW = np.random.normal(0, np.sqrt(dt))
            drift = kappa * (theta - r_t) * dt
            diffusion = sigma * np.sqrt(max(r_t, 0)) * dW
            rates_CIR[t, m] = max(r_t + drift + diffusion, 0)
    return rates_CIR
