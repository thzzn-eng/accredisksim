import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk # Import tkinter

# Constants
G = 6.674e-8        # gravitational constant in cgs
sigma = 5.67e-5     # Stefan-Boltzmann constant in cgs
M = 1.0e33          # example: solar mass in grams
R = 1.0e11          # example: 1 AU in cm
k = 10              # arbitrary scale for alpha contribution

# Placeholder for the accretion disk simulation function
def run_accretion_simulation(mdot, alpha, M_const, R_const, G_const, sigma_const, k_const, global_temp_min, global_temp_max):
    """
    Simulates an accretion disk with a visual animation based on the given parameters.
    Displays simulation parameters in a separate window.
    """
    # 1. Calculate temperature for the clicked point
    F_alpha_val = 1 + k_const * alpha
    if R_const == 0:
        current_temp = 0
    else:
        Q_plus_val = (3 * G_const * M_const * mdot) / (8 * np.pi * sigma_const * R_const**3) * F_alpha_val
        current_temp = Q_plus_val**0.25 if Q_plus_val >= 0 else 0

    # Create a separate window for information
    info_window = tk.Toplevel()
    info_window.title("Simulation Parameters")
    info_window.geometry("300x100") # Adjust size as needed

    tk.Label(info_window, text=f"Temperature: {current_temp:.0f} K", font=("Arial", 10)).pack(pady=2)
    tk.Label(info_window, text=f"Mass Accretion Rate (Mdot): {mdot:.1e} g/s", font=("Arial", 10)).pack(pady=2)
    tk.Label(info_window, text=f"Viscosity Parameter (Alpha): {alpha:.2f}", font=("Arial", 10)).pack(pady=2)

    # 2. Create animation window and canvas
    sim_window = tk.Toplevel()
    sim_window.title("Accretion Disk Animation")
    # Ensure info_window closes when sim_window closes
    def on_sim_close():
        if info_window.winfo_exists():
            info_window.destroy()
        sim_window.destroy()
    sim_window.protocol("WM_DELETE_WINDOW", on_sim_close)

    canvas_width = 500
    canvas_height = 500
    canvas = tk.Canvas(sim_window, width=canvas_width, height=canvas_height, bg='black')
    canvas.pack()

    center_x, center_y = canvas_width / 2, canvas_height / 2
    black_hole_radius = 20

    # 3. Define color based on temperature
    def get_color(temp, min_t, max_t):
        if max_t == min_t: # Avoid division by zero if temp range is zero
            norm_temp = 0.5 if temp >= min_t else 0
        else:
            norm_temp = (temp - min_t) / (max_t - min_t)
        norm_temp = max(0, min(1, norm_temp)) # Clamp to [0,1]

        if norm_temp < 0.33: # Cooler: Dark Red to Red
            r = int(150 + 105 * (norm_temp / 0.33))
            g = 0
            b = 0
        elif norm_temp < 0.66: # Medium: Red to Orange/Yellow
            r = 255
            g = int(255 * ((norm_temp - 0.33) / 0.33))
            b = 0
        else: # Hotter: Yellow to Bright White
            r = 255
            g = 255
            b = int(255 * ((norm_temp - 0.66) / 0.34)) # Ensure b can reach 255
        return f'#{r:02x}{g:02x}{b:02x}'

    disk_color = get_color(current_temp, global_temp_min, global_temp_max)

    # 4. Define speed based on temperature
    if global_temp_max == global_temp_min:
        norm_speed_factor = 1.0
    else:
        # Scale speed: 0.5x to 2.5x of base speed
        norm_speed_factor = 0.5 + 2.0 * ((current_temp - global_temp_min) / (global_temp_max - global_temp_min))
    norm_speed_factor = max(0.1, min(3.0, norm_speed_factor)) # Clamp speed factor

    base_angular_speed = 0.005 # radians per frame, reduced for smoother visuals

    # 5. Disk particles/rings setup
    particles = []
    num_rings = 10
    particles_per_ring = 25 # Increased particles for denser look
    min_disk_radius = black_hole_radius + 15
    max_disk_radius = canvas_width / 2 - 40
    
    for i in range(num_rings):
        # Non-linear distribution of rings - more dense towards the center
        ring_pos_factor = (i / (num_rings - 1 if num_rings > 1 else 1))**1.5
        ring_radius = min_disk_radius + (max_disk_radius - min_disk_radius) * ring_pos_factor
        
        # Keplerian-like speed falloff (v ~ 1/sqrt(r)), modulated by temperature
        # Ensure ring_radius is not zero if min_disk_radius can be very small
        speed_falloff = (max_disk_radius / ring_radius)**0.7 if ring_radius > 0 else 1
        ring_angular_speed = base_angular_speed * speed_falloff * norm_speed_factor
        
        for j in range(particles_per_ring):
            angle = (2 * np.pi / particles_per_ring) * j + (np.pi / particles_per_ring * (i % 2)) # Offset alternate rings
            particles.append({
                'id': None,
                'radius': ring_radius,
                'angle': angle,
                'speed': ring_angular_speed,
                'size': max(1.5, 4 - (ring_radius / max_disk_radius) * 3) # Particles get smaller further out
            })

    # 6. Animation loop function
    def update_animation():
        if not sim_window.winfo_exists(): # Stop if window closed
            if info_window.winfo_exists(): # Ensure info window is also closed
                info_window.destroy()
            return
            
        canvas.delete("particle") 

        # Draw black hole (static, but redraw if clearing whole canvas)
        canvas.create_oval(
            center_x - black_hole_radius, center_y - black_hole_radius,
            center_x + black_hole_radius, center_y + black_hole_radius,
            fill='gray10', outline='gray5', tags="bh"
        )
        canvas.create_oval( # Innermost part
            center_x - black_hole_radius/2, center_y - black_hole_radius/2,
            center_x + black_hole_radius/2, center_y + black_hole_radius/2,
            fill='black', tags="bh"
        )

        for p in particles:
            p['angle'] += p['speed']
            # p['angle'] %= (2 * np.pi) # Keep angle in [0, 2pi)

            x = center_x + p['radius'] * np.cos(p['angle'])
            y = center_y + p['radius'] * np.sin(p['angle'])
            
            p_size = p['size']
            # Use a slightly darker outline for particles for definition
            outline_color = "gray20" if disk_color == "#000000" else disk_color 
            p['id'] = canvas.create_oval(
                x - p_size, y - p_size, x + p_size, y + p_size,
                fill=disk_color, outline=outline_color, tags="particle"
            )
        
        sim_window.after(20, update_animation) # ~50 FPS

    update_animation()


# Grid setup
mdot_vals = np.linspace(1e16, 1e19, 100)  # g/s
alpha_vals = np.linspace(0.01, 0.3, 100)  # dimensionless
Mdot, Alpha = np.meshgrid(mdot_vals, alpha_vals)

# Event handler for mouse clicks on the heatmap
def onclick(event, target_ax, data_arrays, sim_constants_tuple): # Renamed for clarity
    mdot_vals_local, alpha_vals_local = data_arrays
    # Unpack all constants including new temp_min and temp_max
    M_local, R_local, G_local, sigma_local, k_local, temp_min_global, temp_max_global = sim_constants_tuple

    if event.inaxes == target_ax:
        clicked_mdot_val = event.xdata
        clicked_alpha_val = event.ydata

        if clicked_mdot_val is None or clicked_alpha_val is None:
            return

        # Find the closest grid values from the original 1D arrays
        actual_mdot = mdot_vals_local[np.argmin(np.abs(mdot_vals_local - clicked_mdot_val))]
        actual_alpha = alpha_vals_local[np.argmin(np.abs(alpha_vals_local - clicked_alpha_val))]

        print(f"\nClicked heatmap at Mdot_approx={clicked_mdot_val:.2e}, Alpha_approx={clicked_alpha_val:.3f}")
        print(f"Using nearest grid point for simulation: Mdot = {actual_mdot:.2e} g/s, Alpha = {actual_alpha:.3f}")

        run_accretion_simulation(actual_mdot, actual_alpha, M_local, R_local, G_local, sigma_local, k_local, temp_min_global, temp_max_global)

# Temperature function
F_alpha = 1 + k * Alpha
Q_plus = (3 * G * M * Mdot) / (8 * np.pi * sigma * R**3) * F_alpha
Temperature = Q_plus**0.25

# Plot heatmap
fig = plt.figure(figsize=(8, 6)) # Get fig object to attach event listener and manage axes
ax = fig.add_subplot(111) # Create an axes for the heatmap

heatmap = ax.pcolormesh(Mdot, Alpha, Temperature, shading='auto', cmap='inferno') # Plot on the created axes

plt.colorbar(heatmap, label='Temperature (K)')
plt.xlabel('Mass Accretion Rate (g/s)')
plt.ylabel('Viscosity Parameter (α)')
plt.title('Accretion Disk Temperature Heatmap (Click for simulation parameters)') # Updated title

# Connect the click event to the handler
# Pass Temperature.min() and Temperature.max() to onclick
fig.canvas.mpl_connect(
    'button_press_event',
    lambda event: onclick(event, ax, (mdot_vals, alpha_vals), (M, R, G, sigma, k, Temperature.min(), Temperature.max()))
)

plt.show()
