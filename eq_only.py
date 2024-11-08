

# Python script for motor sizing calculations

# Given Data
import math

# Barrel dimensions
D_tank = 0.585  # Diameter of the tank in meters
H_tank = 0.93   # Height of the tank in meters

# Impeller dimensions
D_impeller = 0.8  # Diameter of the impeller in meters
N_rpm = 1700        # Rotational speed in RPM

# Fluid properties
rho = 1000       # Density in kg/m^3
mu_cP = 5000     # Viscosity in cP
mu = mu_cP / 1000  # Convert cP to Pa·s

# Constants
efficiency = 0.85  # IE3 85% - 90%
safety_factor = 1.2  # 20% safety factor
K = 646             # Constant for paddle impeller


print(f"RPM: {N_rpm} ")
print(f"Diametro aletas revolvedor en cm: {D_impeller * 100}")
print(f"Viscosidad asumida: {mu_cP} cP")
print("-----------------------")

# Calculations
# Convert N from RPM to RPS
N = N_rpm / 60  # Rotational speed in rps

# Calculate Reynolds number
Re = (rho * N * D_impeller**2) / mu

# Calculate Power number
Po = K / Re

# Calculate power requirement
P = Po * rho * N**3 * D_impeller**5  # Power in Watts

# Adjust for motor efficiency and safety factor
P_adjusted = (P / efficiency) * safety_factor

# Print results
print(f"Reynolds number (Re): {Re:.2f}")
print(f"Power number (Po): {Po:.2f}")
print(f"Required power (P): {P:.2f} Watts")
print(f"Adjusted power with efficiency and safety factor: {P_adjusted:.2f} Watts")

# Suggest motor power rating
motor_power_rating = math.ceil(P_adjusted / 10) * 10  # Round up to nearest 10 Watts
print(f"Suggested motor power rating: {motor_power_rating} Watts")
# Supongamos que P_adjusted es la potencia en Watts calculada previamente
hp = P_adjusted / 745.699872  # Convierte Watts a HP

print(f"Potencia ajustada: {P_adjusted:.2f} Watts o {hp:.2f} caballos de fuerza (HP)")
