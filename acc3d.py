import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # Import the 3D plotting toolkit

# Constants (same as acc.py)
G = 6.674e-8        # gravitational constant in cgs
sigma = 5.67e-5     # Stefan-Boltzmann constant in cgs
M = 1.0e33          # example: solar mass in grams
R = 1.0e11          # example: 1 AU in cm
k = 10              # arbitrary scale for alpha contribution

# Grid setup (same as acc.py)
mdot_vals = np.linspace(1e16, 1e19, 50)  # g/s (reduced points for 3D clarity)
alpha_vals = np.linspace(0.01, 0.3, 50)  # dimensionless (reduced points for 3D clarity)
Mdot, Alpha = np.meshgrid(mdot_vals, alpha_vals)

# Temperature function (same as acc.py)
F_alpha = 1 + k * Alpha
# Ensure R is not zero to avoid division by zero
if R == 0:
    Q_plus = np.zeros_like(Mdot) # Or handle as an error/default
else:
    Q_plus = (3 * G * M * Mdot) / (8 * np.pi * sigma * R**3) * F_alpha

# Temperature must be non-negative
Temperature = np.where(Q_plus >= 0, Q_plus**0.25, 0)

# 3D Plotting
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Create the 3D surface plot
# X: Mdot, Y: Alpha, Z: Temperature
surf = ax.plot_surface(Mdot, Alpha, Temperature, cmap='inferno', edgecolor='none')

# Add labels and title
ax.set_xlabel('Mass Accretion Rate (Mdot g/s)')
ax.set_ylabel('Viscosity Parameter (Alpha)')
ax.set_zlabel('Temperature (K)')
ax.set_title('3D Accretion Disk Temperature Profile')

# Add a color bar which maps values to colors
fig.colorbar(surf, shrink=0.5, aspect=5, label='Temperature (K)')

# Improve layout and show plot
plt.tight_layout()
plt.show()
