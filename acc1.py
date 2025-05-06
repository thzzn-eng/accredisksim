import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk # Import tkinter

# Constants
G = 6.674e-8        # gravitational constant in cgs
sigma = 5.67e-5     # Stefan-Boltzmann constant in cgs
M = 1.0e33          # example: solar mass in grams
R = 1.0e11          # example: 1 AU in cm (This will be R_outer for the simulation)
k = 10              # arbitrary scale for alpha contribution
c = 3.0e10          # speed of light in cm/s

# Placeholder for the accretion disk simulation function
def run_accretion_simulation(mdot, alpha, M_const, R_outer_const, G_const, sigma_const, k_const): # Removed global_temp_min, global_temp_max
    """
    Simulates an accretion disk with a visual animation based on the given parameters,
    featuring radially-dependent temperature and particle speeds.
    Displays simulation parameters in a separate window.
    """
    # 1. Calculate ISCO (Innermost Stable Circular Orbit)
    # R_in = 6GM/c^2 for Schwarzschild black hole
    if M_const == 0 or G_const == 0 or c == 0:
        R_in_physical = 0
    else:
        R_in_physical = (6 * G_const * M_const) / (c**2)

    F_alpha_factor = 1 + k_const * alpha

    # Create a separate window for information
    info_window = tk.Toplevel()
    info_window.title("Simulation Parameters")
    info_window.geometry("350x150") # Adjust size as needed

    # Display basic parameters
    tk.Label(info_window, text=f"Mass Accretion Rate (Mdot): {mdot:.1e} g/s", font=("Arial", 10)).pack(pady=2)
    tk.Label(info_window, text=f"Viscosity Parameter (Alpha): {alpha:.2f}", font=("Arial", 10)).pack(pady=2)
    tk.Label(info_window, text=f"Outer Disk Radius (R_outer): {R_outer_const:.1e} cm", font=("Arial", 10)).pack(pady=2)
    tk.Label(info_window, text=f"ISCO Radius (R_in): {R_in_physical:.1e} cm", font=("Arial", 10)).pack(pady=2)
    
    # Placeholder for temperatures, will be updated after calculation
    temp_info_label = tk.Label(info_window, text="Calculating temperatures...", font=("Arial", 10))
    temp_info_label.pack(pady=2)


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
    # Visual representation of black hole / inner edge
    # Scale black_hole_radius visually based on R_in relative to R_outer_const if R_in is significant
    # This is a visual choice, not a direct physical scaling for the BH event horizon itself.
    if R_outer_const > 0 and R_in_physical > 0:
        # Max visual radius for ISCO representation is, say, 1/3 of min_disk_radius_canvas
        max_isco_viz_radius = (canvas_width / 2 - 40) / 6
        # Smallest canvas radius for particles
        min_disk_radius_canvas_ref = 20 + 15 
        # Scale R_in_physical to canvas size, but cap it.
        # This scaling factor maps R_outer_const to max_disk_radius_canvas
        physical_to_canvas_scale = (canvas_width / 2 - 40) / R_outer_const
        black_hole_radius_visual = min(max(5, R_in_physical * physical_to_canvas_scale), max_isco_viz_radius)
        # Ensure min_disk_radius_canvas is always larger than the visual black hole
        min_disk_radius_canvas = black_hole_radius_visual + 15
    else:
        black_hole_radius_visual = 20
        min_disk_radius_canvas = black_hole_radius_visual + 15

    max_disk_radius_canvas = canvas_width / 2 - 40


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

    # disk_color will be set per ring later

    # 4. Speed calculation will be per ring

    base_angular_speed = 0.005 # radians per frame

    # 5. Disk particles/rings setup
    particles = []
    num_rings = 20 # Increased rings for better radial gradient
    particles_per_ring = 30
    
    ring_data = [] # To store physical radius and temperature for each ring

    # Map canvas radii to physical radii
    # Smallest physical radius corresponds to min_disk_radius_canvas
    # Largest physical radius corresponds to R_outer_const at max_disk_radius_canvas
    
    # Ensure R_physical_min is at least R_in_physical, or slightly larger for stability
    R_physical_min_for_sim = max(R_in_physical, R_outer_const * (min_disk_radius_canvas / max_disk_radius_canvas))
    if R_physical_min_for_sim == 0 and R_outer_const > 0 : # Edge case if R_in is 0
        R_physical_min_for_sim = R_outer_const * 0.05 # Start at 5% of R_outer if R_in is zero

    for i in range(num_rings):
        # Non-linear distribution of rings on canvas - more dense towards the center
        ring_pos_factor_canvas = (i / (num_rings - 1 if num_rings > 1 else 1))**1.5
        canvas_r = min_disk_radius_canvas + (max_disk_radius_canvas - min_disk_radius_canvas) * ring_pos_factor_canvas

        # Map canvas_r to physical_r
        # Linear mapping from [min_disk_radius_canvas, max_disk_radius_canvas] to [R_physical_min_for_sim, R_outer_const]
        if max_disk_radius_canvas == min_disk_radius_canvas: # Avoid division by zero
            physical_r_norm = 0
        else:
            physical_r_norm = (canvas_r - min_disk_radius_canvas) / (max_disk_radius_canvas - min_disk_radius_canvas)
        
        physical_r = R_physical_min_for_sim + (R_outer_const - R_physical_min_for_sim) * physical_r_norm
        
        current_ring_temp = 0
        if physical_r > R_in_physical and physical_r > 0 and sigma_const > 0: # Check physical_r > R_in_physical
            # Radially-dependent temperature formula
            # T(r) = [ (3GM Mdot / (8 pi sigma r^3)) * (1 - sqrt(R_in / r)) * F_alpha ] ^ 0.25
            term1 = (3 * G_const * M_const * mdot) / (8 * np.pi * sigma_const * physical_r**3)
            term2 = (1 - (R_in_physical / physical_r)**0.5) if physical_r > R_in_physical else 0 # Ensure R_in/r <=1
            Q_plus_radial = term1 * term2 * F_alpha_factor
            current_ring_temp = Q_plus_radial**0.25 if Q_plus_radial >= 0 else 0
        
        ring_data.append({'canvas_r': canvas_r, 'physical_r': physical_r, 'temp': current_ring_temp})

    # Determine min and max temperatures for this simulation instance for color scaling
    all_temps = [r['temp'] for r in ring_data if r['temp'] > 0]
    if not all_temps: # If all temps are zero (e.g., mdot is zero or R_in is too large)
        min_sim_temp, max_sim_temp = 0, 1 # Avoid division by zero in get_color
    else:
        min_sim_temp = min(all_temps)
        max_sim_temp = max(all_temps)
    
    # Update temperature info in the info window
    T_at_R_physical_min_for_sim = ring_data[0]['temp'] if ring_data else 0
    T_at_R_outer_const = ring_data[-1]['temp'] if ring_data else 0
    temp_info_label.config(text=f"T_inner_sim: {T_at_R_physical_min_for_sim:.0f} K, T_outer_sim: {T_at_R_outer_const:.0f} K")


    for i in range(num_rings):
        ring_info = ring_data[i]
        canvas_r = ring_info['canvas_r']
        physical_r = ring_info['physical_r']
        T_ring = ring_info['temp']

        ring_color = get_color(T_ring, min_sim_temp, max_sim_temp)

        # Speed scaling based on ring's temperature relative to sim's min/max temp
        if max_sim_temp == min_sim_temp:
            norm_temp_for_speed = 0.5
        else:
            norm_temp_for_speed = (T_ring - min_sim_temp) / (max_sim_temp - min_sim_temp)
        
        # Scale speed: 0.5x to 2.5x of base Keplerian speed for this radius
        temp_speed_factor = 0.5 + 2.0 * norm_temp_for_speed
        temp_speed_factor = max(0.1, min(3.0, temp_speed_factor))

        # Keplerian angular speed falloff: omega ~ r^(-3/2)
        # Use R_outer_const as the reference for the base_angular_speed
        if physical_r > 0 and R_outer_const > 0:
            # speed_falloff = (R_outer_const / physical_r)**1.5 # More physically based for angular speed
            # To prevent extreme speeds at very small physical_r if R_outer_const is large:
            # Use a reference physical radius for the base_angular_speed, e.g., R_outer_const
            # Or, scale relative to the largest radius in the simulation if that's more stable.
            # Let's use R_outer_const as the radius where base_angular_speed is defined.
            keplerian_factor = (R_outer_const / physical_r)**1.5 if physical_r > 0 else 1.0
        else:
            keplerian_factor = 1.0
        
        # Cap keplerian_factor to avoid excessively high speeds if physical_r is very small
        # e.g. if physical_r is 1% of R_outer_const, (100)^1.5 = 1000 times faster.
        # This cap depends on how small physical_r can get relative to R_outer_const.
        # Max speedup of, say, 20-50x the base angular speed at R_outer.
        keplerian_factor = min(keplerian_factor, 50.0)


        ring_angular_speed = base_angular_speed * keplerian_factor * temp_speed_factor
        
        for j in range(particles_per_ring):
            angle = (2 * np.pi / particles_per_ring) * j + (np.pi / particles_per_ring * (i % 2))
            particles.append({
                'id': None,
                'radius': canvas_r, # Use canvas radius for drawing
                'angle': angle,
                'speed': ring_angular_speed,
                'color': ring_color, # Store color per particle/ring
                'size': max(1.5, 4 - (canvas_r / max_disk_radius_canvas) * 3)
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
            center_x - black_hole_radius_visual, center_y - black_hole_radius_visual,
            center_x + black_hole_radius_visual, center_y + black_hole_radius_visual,
            fill='gray10', outline='gray5', tags="bh"
        )
        canvas.create_oval( # Innermost part
            center_x - black_hole_radius_visual/2, center_y - black_hole_radius_visual/2,
            center_x + black_hole_radius_visual/2, center_y + black_hole_radius_visual/2,
            fill='black', tags="bh"
        )

        for p in particles:
            p['angle'] += p['speed']
            # p['angle'] %= (2 * np.pi) # Keep angle in [0, 2pi)

            x = center_x + p['radius'] * np.cos(p['angle'])
            y = center_y + p['radius'] * np.sin(p['angle'])
            
            p_size = p['size']
            # Use a slightly darker outline for particles for definition
            outline_color = "gray20" if p['color'] == "#000000" else p['color']
            p['id'] = canvas.create_oval(
                x - p_size, y - p_size, x + p_size, y + p_size,
                fill=p['color'], outline=outline_color, tags="particle" # Use particle's own color
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
    M_local, R_local, G_local, sigma_local, k_local = sim_constants_tuple

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

        # Removed temp_min_global, temp_max_global from the call
        run_accretion_simulation(actual_mdot, actual_alpha, M_local, R_local, G_local, sigma_local, k_local)

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
    # Removed Temperature.min() and Temperature.max() from the lambda's capture and pass-through
    lambda event: onclick(event, ax, (mdot_vals, alpha_vals), (M, R, G, sigma, k))
)

plt.show()
