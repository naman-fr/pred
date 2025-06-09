# unwrap.py

import numpy as np

# Speed of light in m/s
C = 299792458.0

def weighted_crt_unwrap(phases, freqs, noise_vars=None, max_range=100.0):
    """
    Estimate range from wrapped phases using a weighted CRT approach.
    Args:
        phases (ndarray): Wrapped phases (radians) shape (M,).
        freqs (ndarray): Frequencies (Hz) shape (M,).
        noise_vars (ndarray or float): Variances of noise for each phase. 
                                       If None, equal weighting is used.
        max_range (float): Maximum search range (m) to bound integer search.
    Returns:
        best_d (float): Estimated distance (m).
    """
    M = len(freqs)
    # Set weights: w_i = 1/(2 * sigma_i^2)
    if noise_vars is None:
        weights = np.ones(M)
    else:
        # If a single variance provided, broadcast; else elementwise.
        vars = noise_vars if np.ndim(noise_vars) > 0 else np.full(M, noise_vars)
        weights = 1.0 / (2.0 * vars)
    # Reference frequency index (0)
    f0, phi0 = freqs[0], phases[0]
    # Compute phi0 base distance ignoring k0
    base_d0 = (phi0 / (2*np.pi)) * (C / f0)
    # Determine plausible integer range for k0
    lambda0 = C / f0
    k0_min = int(np.ceil((-base_d0) / lambda0))
    k0_max = int(np.floor((max_range - base_d0) / lambda0))
    best_score = float('inf')
    best_d = 0.0
    # Search over possible k0
    for k0 in range(k0_min, k0_max+1):
        d0 = base_d0 + k0 * lambda0  # candidate distance from freq0
        # Compute implied k and d for other frequencies
        ds = [d0]
        for i in range(1, M):
            fi, phii = freqs[i], phases[i]
            # Estimate ki to align phase with d0
            lambda_i = C / fi
            # number of whole wavelengths to match distance d0
            ki = int(np.round((d0 - (phii/(2*np.pi))*lambda_i) / lambda_i))
            di = (phii/(2*np.pi))*lambda_i + ki * lambda_i
            ds.append(di)
        ds = np.array(ds)
        # Weighted mean distance
        d_mean = np.average(ds, weights=weights)
        # Weighted sum-of-squares error
        score = np.sum(weights * (ds - d_mean)**2)
        if score < best_score:
            best_score = score
            best_d = d_mean
    return best_d
