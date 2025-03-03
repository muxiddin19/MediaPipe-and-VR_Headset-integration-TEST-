# utils.py
from filterpy.kalman import KalmanFilter
import numpy as np

def initialize_kalman():
    kf = KalmanFilter(dim_x=3, dim_z=3)
    kf.x = np.array([0., 0., 0.])
    kf.F = np.eye(3)
    kf.H = np.eye(3)
    kf.P *= 1000.
    kf.R = 5
    kf.Q = 0.1
    return kf
