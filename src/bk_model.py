
def simulate_BK_trajectories(r0, alpha, sigma, TAMAR_view, M ,T_years, N, seed=123):

    """
    Simulates M Black–Karasinski interest rate trajectories over N time steps (total time = T_years).

    Parameters:
    - r0: Initial interest rate
    - alpha: Mean reversion speed
    - sigma: Volatility
    - TAMAR_view: List or array of theta(t), expected mean rate path (length N)
    - M: Number of simulation paths
    - T_years: Total simulation time in years
    - N: Number of time steps
    - seed: Random seed for reproducibility

    Returns:
    - rates: Array of shape (N+1, M) with interest rate paths


    """
    dt= T_years/N
    np.random.seed (seed)
    rates_BK = np.zeros((N+1, M))
    rates_BK [0,:] = r0

    for m in range (M):
        for t in range (1, N+1):
            r_t = np.log(rates_BK[t - 1, m])
            theta_t = np.log (TAMAR_view[t - 1])
            dW = np.random.normal(0, np.sqrt(dt))
            mean_reversion = alpha * (theta_t - r_t) * dt
            diffusion = sigma * dW
            x_next = r_t + mean_reversion + diffusion
            rates_BK[t, m] = np.exp(x_next)
    return rates_BK
