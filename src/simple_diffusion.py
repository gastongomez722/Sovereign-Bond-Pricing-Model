
def simulate_trajectories (sigma, r0, T_years, N, M ,seed = 123):
    """
    This function aims to simulate several interst rate paths under a simple model in which the interest rate is determined by exogenous normaly distributed shocks.

    params:

    sigma: Annualized volatility
    r0: Initial interest rate
    T: Total time in years
    N: total steps
    seed: Uses 123 as default seed
    Returns:
    - rates: Array of shape (N+1, M) with interest rate paths
    """
    dt = T_years/N
    np.random.seed(seed)
    trajectories = np.zeros((N+1,M))
    trajectories [0, :] = r0

    for m in range(M):
        for t in range (1, N+1):
            dW = np.random.normal(0, np.sqrt(dt))
            # Use -drift to ensure that a positive drift parameter makes rates fall.
            #r_t = trajectories[t - 1, m]
            dr_t = (sigma) * dW
            # Enforce non-negativity.
            trajectories[t, m] = max(0, trajectories[t - 1, m] + dr_t)
    return trajectories