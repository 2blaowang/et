import numpy as np
import matplotlib.pyplot as plt

# 参数设置
frequency = 1  # 频率 (Hz)
amplitude = 1  # 振幅
phase = 0      # 相位 (弧度)
sampling_rate = 1000  # 采样率 (Hz)
duration = 1   # 持续时间 (秒)

# 生成时间轴
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# 生成正弦波
y = amplitude * np.sin(2 * np.pi * frequency * t + phase)

# 绘制正弦波
plt.plot(t, y)
plt.title('正弦波')
plt.xlabel('时间 (秒)')
plt.ylabel('振幅')
plt.grid(True)
plt.show()