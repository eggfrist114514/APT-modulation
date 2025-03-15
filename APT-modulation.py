import numpy as np
import wave
import struct
from PIL import Image

# 打印项目信息
# Print project information
print("""
⠀⠀⠀⠀ ⣶⣿⣿⣿⣿⣿⣿⣿⣿⣄
⠀⠀⣰⣿⣿⣿⡿⠟⠛⠛⠛⠿⣿⣿⣿
⠀⠀⢸⣿⣿⣥⣤⠀⠀⠀⣀⣀⠀⠘⣿⡏
⠀⠀⠈⡟⠿⠶⠂⠀⠀⠀⠶⠆⠀⠀⣿⠃
⠀⠀⠀⣷⡀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠂
⠀⠀⠀⠀⢻⣦⣤⣥⣀
⠀⠀⠀⠀⠀⣿⣿⣛⡁⠀⠀⠀⠀⡀
⠀⣀⣴⠃⠘⣿⣿⣿⡿⠀⠀⠀⠀⣼⣿⣶⣄
⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⢀⣠⣾⣿⣿⣿⣿
本项目基于apt-encode®制作者:硝酸氢二铵
This project is based on the apt-encode ® manufacturer: diammonium hydrogen nitrate
由于python精度的影响,目前就更新止步于此,终止版本BATA-1.2
Due to the impact of python precision, the current update stops here and terminates version BATA-1.2.
""")

# 定义同步字
# Define synchronization words
sync_A = [0, 0, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sync_B = [0, 0, 0, 0, 255, 255, 255, 0, 0, 255, 255, 255, 0, 0, 255, 255, 255, 0, 0, 255, 255, 255, 0, 0, 255, 255, 255, 0, 0, 255, 255, 255, 0, 0, 255, 255, 255, 0, 0]

# 定义变量
# Define variables
sync_signal_freq_A = 1350
sync_signal_freq_B = 1550
carrier_freq = 2400
T = 0.01  # 同步信号的持续时间为0.02秒
# The duration of the synchronization signal is 0.02 seconds
sample_rate = 44100

# 计算每个样本的持续时间 t
# Calculate the duration of each sample t
t = (0.5+0.0605) / (2080 - (T * 2080))

# 初始化全局相位
# Initialize global phases
phase_A = 0.0
phase_B = 0.0
phase_carrier = 0.0

# 获取输入的图像路径
# Get the input image paths
raw_image_pathA = input("请输入第一张图片的路径(Enter the path to the first picture)：")
# Enter the path of the first image:
raw_image_pathB = input("请输入第二张图片的路径(Enter the path to the second picture)：")
# Enter the path of the second image:

# 打开图像并转换为灰度图像
# Open the images and convert them to grayscale
imageA = Image.open(raw_image_pathA).convert("L")
imageB = Image.open(raw_image_pathB).convert("L")

# 调整图像大小
# Resize the images
new_width = 909
new_heightA = int(imageA.height * (new_width / imageA.width))
imageA = imageA.resize((new_width, new_heightA), Image.LANCZOS)
imageB = imageB.resize((new_width, new_heightA), Image.LANCZOS)

# 打开音频文件进行写入
# Open the audio file for writing
with wave.open("APT.wav", "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)

    # 遍历图像的每一行
    # Iterate over each row of the image
    for y in range(new_heightA):
        # 添加同步字A
        # Add synchronization word A
        for value in sync_A:
            mapped_gray = value / 255 * 0.7
            for i in range(int(t * sample_rate)):
                sample_carrier = mapped_gray * np.sin(phase_carrier)
                wav_file.writeframes(struct.pack("<h", int(sample_carrier * 32767)))
                phase_carrier = (phase_carrier + 2 * np.pi * carrier_freq / sample_rate) % (2 * np.pi)

        # 添加同步信号A
        # Add synchronization signal A
        for i in range(int(T * sample_rate)):
            sample_A = 0.7 * np.sin(phase_A)  # 同步信号A的幅度为0.7
            # The amplitude of synchronization signal A is 0.7
            wav_file.writeframes(struct.pack("<h", int(sample_A * 32767)))
            phase_A = (phase_A + 2 * np.pi * sync_signal_freq_A / sample_rate) % (2 * np.pi)

        # 添加图像A的一行灰度值
        # Add a row of grayscale values of image A
        for x in range(new_width):
            gray = imageA.getpixel((x, y))
            mapped_gray = gray / 255 * 0.7
            for i in range(int(t * sample_rate)):
                sample_carrier = mapped_gray * np.sin(phase_carrier)
                wav_file.writeframes(struct.pack("<h", int(sample_carrier * 32767)))
                phase_carrier = (phase_carrier + 2 * np.pi * carrier_freq / sample_rate) % (2 * np.pi)

        # 添加同步字B
        # Add synchronization word B
        for value in sync_B:
            mapped_gray = value / 255 * 0.7
            for i in range(int(t * sample_rate)):
                sample_carrier = mapped_gray * np.sin(phase_carrier)
                wav_file.writeframes(struct.pack("<h", int(sample_carrier * 32767)))
                phase_carrier = (phase_carrier + 2 * np.pi * carrier_freq / sample_rate) % (2 * np.pi)

        # 添加同步信号B
        # Add synchronization signal B
        for i in range(int(T * sample_rate)):
            sample_B = 0.7 * np.sin(phase_B)  # 同步信号B的幅度为0.7
            # The amplitude of synchronization signal B is 0.7
            wav_file.writeframes(struct.pack("<h", int(sample_B * 32767)))
            phase_B = (phase_B + 2 * np.pi * sync_signal_freq_B / sample_rate) % (2 * np.pi)

        # 添加图像B的一行灰度值
        # Add a row of grayscale values of image B
        for x in range(new_width):
            gray = imageB.getpixel((x, y))
            mapped_gray = gray / 255 * 0.7
            for i in range(int(t * sample_rate)):
                sample_carrier = mapped_gray * np.sin(phase_carrier)
                wav_file.writeframes(struct.pack("<h", int(sample_carrier * 32767)))
                phase_carrier = (phase_carrier + 2 * np.pi * carrier_freq / sample_rate) % (2 * np.pi)

        # 打印进度
        # Print progress
        print(f"处理进度(Progress): {y + 1}/{new_heightA}")
        # Processing progress:

print("生成完成(Build complete)")
# Generation completed
"""
dfdeddeefededdfdedfdefdfrfdfefeeedeeeefffdefdefdefdfedefd
"""
