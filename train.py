# train.py

import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import HuberRegressor
from simulate import generate_dataset

def train_models(freqs, num_samples=5000, noise_std=0.02):
    """
    Train and save regression models to predict range from phases.
    Args:
        freqs (ndarray): Frequencies (Hz) for simulation.
        num_samples (int): Number of synthetic training samples.
        noise_std (float): Phase noise std for training data.
    """
    # Generate synthetic training data
    X, y = generate_dataset(num_samples, freqs, max_range=100.0, noise_std=noise_std)
    # Prepare features: input as phase vector (could also use sin/cos of phases)
    # Here we use phases directly (ensure shape NxM)
    # Initialize regressors
    rf = RandomForestRegressor(n_estimators=100, random_state=0)
    huber = HuberRegressor(epsilon=1.35, max_iter=1000)
    # Train models
    rf.fit(X, y)
    huber.fit(X, y)
    # Save trained models to files
    with open('rf_model.pkl', 'wb') as f:
        pickle.dump(rf, f)
    with open('huber_model.pkl', 'wb') as f:
        pickle.dump(huber, f)
    print("Models trained and saved (RandomForest and Huber).")

if __name__ == "__main__":
    # Example usage: define frequencies (Hz) and train
    freqs = np.array([5e9, 5.5e9, 6e9])  # e.g., three GHz-range carriers
    train_models(freqs)
