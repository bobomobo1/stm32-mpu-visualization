import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import re
import time
import matplotlib

matplotlib.use('TkAgg')  # Or 'Qt5Agg' if you prefer

# === Serial Port Setup ===
ser = serial.Serial('/dev/ttyACM0', 115200)

# === Constants ===
GRAVITY_G = 1.08       # gravity in g's based on your resting reading
G_TO_MS2 = 9.81        # convert g to m/s²
DAMPING = 0.90         # velocity damping factor to reduce drift

# === Buffers ===
buffer_len = 200
az_list = deque([0.0]*buffer_len, maxlen=buffer_len)
z_pos = deque([0.0]*buffer_len, maxlen=buffer_len)

# === State Variables ===
vz = 0.0
z = 0.0
last_time = time.time()

# === Regex Pattern ===
pattern = re.compile(r"Az:\s*(-?\d+\.\d+)")

# === Plot Setup ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
line_az, = ax1.plot(az_list, label='Acceleration (m/s²)')
line_z, = ax2.plot(z_pos, label='Position (m)', color='orange')

ax1.set_ylim(-10, 10)
ax2.set_ylim(-1.0, 1.0)
ax1.set_title("Acceleration Z")
ax2.set_title("Estimated Position Z")
ax1.set_ylabel("m/s²")
ax2.set_ylabel("meters")
ax2.set_xlabel("Time")
ax1.grid(True)
ax2.grid(True)

def update(frame):
    global vz, z, last_time

    try:
        line_data = ser.readline().decode(errors='ignore').strip()
        match = pattern.match(line_data)

        if match:
            raw_az_g = float(match.group(1))
            az_g = raw_az_g - GRAVITY_G
            az_g = -az_g
            az = az_g * G_TO_MS2

            now = time.time()
            dt = now - last_time
            last_time = now

            # Integrate
            vz += az * dt
            vz *= DAMPING
            z += vz * dt

            # Store data
            az_list.append(az)
            z_pos.append(z)

            # Update plot data
            line_az.set_ydata(az_list)
            line_az.set_xdata(range(len(az_list)))

            line_z.set_ydata(z_pos)
            line_z.set_xdata(range(len(z_pos)))

    except Exception as e:
        print(f"[ERROR] {e}")

    return line_az, line_z

ani = animation.FuncAnimation(fig, update, interval=50)
plt.tight_layout()
plt.show()

