# simulate.py

import numpy as np

C = 3e8  # Speed of light (m/s)

def wrap_phase(phase):
    """Wrap phase to [-pi, +pi]."""
    return (phase + np.pi) % (2 * np.pi) - np.pi

def simulate_phase_measurement(distance, freqs, noise_std=0.01):
    """
    Simulate wrapped phase measurements for a given distance and frequencies.
    Args:
        distance (float): True target range in meters.
        freqs (array): Carrier frequencies in Hz (e.g. [f1, f2, ...]).
        noise_std (float): Standard deviation of Gaussian noise (radians).
    Returns:
        phases (ndarray): Wrapped phases (radians) of shape (len(freqs),).
    """
    # Compute true phase for each frequency: phi = 2*pi*f*d/c
    true_phase = 2 * np.pi * freqs * distance / C
    # Wrap to [0,2pi) then to [-pi,pi]
    wrapped = wrap_phase(true_phase)
    # Add independent Gaussian noise to each phase
    noisy = wrapped + np.random.normal(0, noise_std, size=wrapped.shape)
    return wrap_phase(noisy)

def generate_dataset(num_samples, freqs, max_range=100.0, noise_std=0.01):
    """
    Generate synthetic dataset of phase measurements and ranges.
    Args:
        num_samples (int): Number of random samples.
        freqs (array): Frequencies in Hz.
        max_range (float): Maximum true range (m).
        noise_std (float): Noise standard deviation (radians).
    Returns:
        X (ndarray): Array of shape (num_samples, len(freqs)) of phases.
        y (ndarray): Array of shape (num_samples,) of true ranges.
    """
    # Random true distances (uniformly in [0, max_range])
    distances = np.random.uniform(0, max_range, size=num_samples)
    # Simulate phases for each sample
    phases = np.array([simulate_phase_measurement(d, freqs, noise_std) for d in distances])
    return phases, distances
