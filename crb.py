# crb.py

import numpy as np
import matplotlib.pyplot as plt

C = 3e8

def crb(freqs, sigma_phi):
    """Compute CRB for range."""
    fisher = np.sum((2*np.pi*freqs/C)**2 / (sigma_phi**2))
    return 1.0 / fisher

if __name__ == "__main__":
    freqs = np.array([5e9,5.5e9,6e9])
    sigmas = np.linspace(0.005,0.05,10)
    bounds = [crb(freqs,s) for s in sigmas]
    plt.plot(sigmas, np.sqrt(bounds), marker="o")
    plt.xlabel("Phase noise σ (rad)")
    plt.ylabel("RMS range bound (m)")
    plt.title("Cramér–Rao Bound vs. Phase-noise")
    plt.grid(True)
    plt.show()
