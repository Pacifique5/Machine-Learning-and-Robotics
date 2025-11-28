import numpy as np
import matplotlib.pyplot as plt

# Baseband and carrier parameters
Am = 100         # Baseband amplitude
Ac = 150         # Carrier amplitude
wm = 200         # Message angular frequency
wc = 3000        # Carrier angular frequency

# Modulation index
m = Am / Ac

# Time axis - Extended to 0.15s to show more message cycles
t = np.linspace(0, 0.15, 5000)

# Signals
message = Am * np.sin(wm * t)
carrier = Ac * np.sin(wc * t)
am_signal = Ac * (1 + m * np.sin(wm * t)) * np.sin(wc * t)

# Envelope detection
upper_env = Ac * (1 + m * np.sin(wm * t))
lower_env = -Ac * (1 + m * np.sin(wm * t))

# Plot message signal
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(t, message)
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
plt.title("Message Signal (Baseband)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

# Plot carrier signal
plt.subplot(3, 1, 2)
plt.plot(t, carrier)
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
plt.title("Carrier Signal")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

# Plot AM modulated signal with envelope
plt.subplot(3, 1, 3)
plt.plot(t, am_signal, label="AM Signal")
plt.plot(t, upper_env, 'r--', label="Upper Envelope")
plt.plot(t, lower_env, 'k--', label="Lower Envelope")
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
plt.title("AM Modulated Signal")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.xlim(0, 0.15)
plt.xticks(np.linspace(0, 0.15, 16))
plt.legend()

plt.tight_layout()
plt.show()
