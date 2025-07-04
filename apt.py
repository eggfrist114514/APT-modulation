import math
import numpy as np
from PIL import Image
import wave
import sys
"""
更新日志:更改了同步信号，幅度，减少杂波
"""
# Utils
print ("本项目基于apt-encode制作者:硝酸氢二铵【MC_blone fo billbill】\n使用方法:python xxx.py image1 image2")
def map_value(value, f1, t1, f2, t2):
    return f2 + ((t2 - f2) * (value - f1)) / (t1 - f1)

def max_val(val1, val2):
    return val1 if val1 > val2 else val2

# Constants and config

CARRIER = 2400
BAUD = 4160
OVERSAMPLE = 3

# Sync words for the left and right images

SYNCA = "000011001100110011001100110011000000000"
SYNCB = "000011100111001110011100111001110011100"

# Image processing

class ImageProcessor:
    def __init__(self, path, maintain_aspect_ratio=True):
        self.path = path
        self.maintain_aspect_ratio = maintain_aspect_ratio
        self.image = None
        self.width = 0
        self.height = 0
        self.pixels = None

    def load(self, target_height=None):
        # Open and convert image to grayscale
        self.image = Image.open(self.path).convert('L')
        
        # Resize image
        if self.maintain_aspect_ratio:
            # Maintain aspect ratio, resize width to 909
            original_width, original_height = self.image.size
            aspect_ratio = original_height / original_width
            new_width = 909
            new_height = int(new_width * aspect_ratio)
            self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
        else:
            # Do not maintain aspect ratio, resize width to 909
            original_width, original_height = self.image.size
            new_width = 909
            new_height = original_height  # Keep original height
            self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
        
        # Adjust height if target_height is provided
        if target_height is not None:
            self.image = self.image.resize((909, target_height), Image.LANCZOS)
        
        self.width, self.height = self.image.size
        self.pixels = np.array(self.image)

    def get_pixel(self, x, y):
        if y >= self.height:
            return 0
        return self.pixels[y, x]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def free(self):
        self.image = None
        self.pixels = None

# Audio processing

class AudioProcessor:
    def __init__(self, wave_file):
        self.wave_file = wave_file
        self.phase_carrier = 0.0  # Continuous phase for carrier

    def write_value(self, value):
        sample_rate = BAUD * OVERSAMPLE
        carrier_freq = CARRIER

        for i in range(OVERSAMPLE):
            # Update phase with continuity
            self.phase_carrier = (self.phase_carrier + 2 * math.pi * carrier_freq / sample_rate) % (2 * math.pi)
            samp = math.sin(self.phase_carrier)
            samp *= map_value(int(value), 0, 255, 0.0, 0.35)

            # Map the sample value from [-1.0, 1.0] to [0, 255]
            buf = int(map_value(samp, -1.0, 1.0, 0, 155))
            self.wave_file.writeframes(np.array([buf], dtype=np.uint8).tobytes())

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py ./image1.pgm ./image2.pgm")
        return 1

    # Create wave file
    wave_file = wave.open('output.wav', 'w')
    wave_file.setnchannels(1)
    wave_file.setsampwidth(1)
    wave_file.setframerate(BAUD * OVERSAMPLE)

    audio_processor = AudioProcessor(wave_file)
    lks=0
    lks1=0
    mode= int(input("请输入模式,0表示带可见光和红外,1表示只有红外\n"))
    gz = int(input("是否故障?0/1"))
    avhrr=0
    avhrr1=0
    forge=0
    # Load images
    img1 = ImageProcessor(sys.argv[1], maintain_aspect_ratio=True)
    img2 = ImageProcessor(sys.argv[2] if len(sys.argv) >= 3 else sys.argv[1], maintain_aspect_ratio=False)
    img1.load()
    img2.load(target_height=img1.get_height())

    height = max_val(img1.get_height(), img2.get_height())

    for line in range(height):
        frame_line = line % 128

        # Sync A
        for i in range(len(SYNCA)):
            char = SYNCA[i]
            val = 0 if char == '0' else 255
            audio_processor.write_value(val)

        # Space A
        if mode==0:
            if lks<99:
                for i in range(47):
                    audio_processor.write_value(0)
                #for i in range(3):
                    #audio_processor.write_value(255)
            else:
                if lks>101:
                    lks=0
                for i in range(47):
                    audio_processor.write_value(255)
                #for i in range(3):
                    #audio_processor.write_value(0)
            lks+=1
        elif mode==1:
            if lks<99:
                for i in range(47):
                    audio_processor.write_value(255)
                #for i in range(3):
                    #audio_processor.write_value(0)
            else:
                if lks>101:
                    lks=0
                for i in range(47):
                    audio_processor.write_value(0)
                #for i in range(3):
                    #audio_processor.write_value(255)
            lks=lks+1
        else:
            print ("条件不合理,请重新输入!")
            sys.exit(main())
        # Image A
        for i in range(img1.get_width()):
            pixel_val = img1.get_pixel(i, line)
            audio_processor.write_value(pixel_val)

        # Telemetry A
        for i in range(45):
            if 0<=avhrr<10:
                audio_processor.write_value(0)
            elif 10<=avhrr<20:
                audio_processor.write_value(57)
            elif 20<=avhrr<30:
                audio_processor.write_value(28)
            elif 30<=avhrr<40:
                audio_processor.write_value(57)
            elif 40<=avhrr<50:
                audio_processor.write_value(85)
            elif 50<=avhrr<60:
                audio_processor.write_value(114)
            elif 60<=avhrr<70:
                audio_processor.write_value(142)
            elif 70<=avhrr<80:
                audio_processor.write_value(171)
            elif 80<=avhrr<90:
                audio_processor.write_value(199)
            elif 90<=avhrr<100:
                audio_processor.write_value(227)
            elif 100<=avhrr<110:
                audio_processor.write_value(255)
            elif 110<=avhrr<120:
                audio_processor.write_value(0)
            elif 120<=avhrr<160:
                audio_processor.write_value(57)
            elif 160<=avhrr<170:
                audio_processor.write_value(0)
            else:
                audio_processor.write_value(85)
        if avhrr>=180:
            avhrr=-1
        avhrr+=1
        # Sync B
        for i in range(len(SYNCB)):
            char = SYNCB[i]
            val = 0 if char == '0' else 255
            audio_processor.write_value(val)
        if gz==0:
        # Space B
            if lks<99:
                for i in range(47):
                    audio_processor.write_value(255)
            #for i in range(3):
                #audio_processor.write_value(0)
            else:
                if lks>101:
                    lks=0
                for i in range(47):
                    audio_processor.write_value(0)
            #for i in range(3):
                #audio_processor.write_value(0)
        else:
        # Space A
            if lks<99:
                for i in range(47):
                    audio_processor.write_value(0)
                #for i in range(3):
                    #audio_processor.write_value(255)
            else:
                if lks>101:
                    lks=0
                for i in range(47):
                    audio_processor.write_value(255)
                #for i in range(3):
                    #audio_processor.write_value(0)

        # Image B
        for i in range(img2.get_width()):
            pixel_val = img2.get_pixel(i, line)
            audio_processor.write_value(pixel_val)

        # Telemetry B

        for i in range(45):
            if 0<=avhrr1<10:
                audio_processor.write_value(114)
            elif 10<=avhrr1<20:
                audio_processor.write_value(57)
            elif 20<=avhrr1<30:
                audio_processor.write_value(28)
            elif 30<=avhrr1<40:
                audio_processor.write_value(57)
            elif 40<=avhrr1<50:
                audio_processor.write_value(85)
            elif 50<=avhrr1<60:
                audio_processor.write_value(114)
            elif 60<=avhrr1<70:
                audio_processor.write_value(142)
            elif 70<=avhrr1<80:
                audio_processor.write_value(171)
            elif 80<=avhrr1<90:
                audio_processor.write_value(199)
            elif 90<=avhrr1<100:
                audio_processor.write_value(227)
            elif 100<=avhrr1<110:
                audio_processor.write_value(255)
            elif 110<=avhrr1<120:
                audio_processor.write_value(0)
            elif 120<=avhrr1<160:
                audio_processor.write_value(57)
            elif 160<=avhrr1<170:
                audio_processor.write_value(114)
            else:
                audio_processor.write_value(85)
        if avhrr1>=180:
            avhrr1=-1
        avhrr1+=1
        if height == 0:
            percentage = 0
        else:
            percentage = (forge / height) * 100
        """转义蓝色字体
        """
        sys.stdout.write(f"\r\x1b[34mProgress\x1b[0m: {percentage:.2f}%")
        sys.stdout.flush()
        forge+=1

        

    img1.free()
    img2.free()
    wave_file.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
