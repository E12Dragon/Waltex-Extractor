# Thanks to @campbellsonic for the wrapRawData script. It was originally written in C#.
# Thanks to @ego-lay-atman-bay for the rewrite in python.
# Thanks to @LolHacksRule for the "weird widths" hack.

import numpy
from tkinter import Tk, filedialog
import tkinter
from PIL import Image
import math
import os

def WaltexImage(path : str, size : tuple = (1024, 1024), colorspace : str = 'rgba4444', premultiplyAlpha : bool = False, dePremultiplyAlpha : bool = False, endian : str = 'little', offset : int = 0) -> Image.Image:
    """Get image from `waltex` file
    Data on image can be found in coorisponding `imagelist` or in `Data/TextureSettings.xml`.
    
    Args:
        path (str): Path to `waltex` image
        size ((width,height), optional): Size of image. Defaults to (1024, 1024).
        colorspace (str, optional): Color spec of image. Defaults to 'rgba4444'.
        premultiplyAlpha (bool, optional): Defaults to False.
        dePremultiplyAlpha (bool, optional): Defaults to False.
        endian (str, optional): Endian mode. Set to 'big' or 1 to use big endian. Defaults to 'little'.
        offset (int, optional): General byte offset. Defaults to 0.
    Returns:
        PIL.Image: Pillow image.
    """
    colorspace = colorspace.lower()
    
    colorOrder = ''
    bytesPerPixel = 0
    bpprgba = []
    
    for i in range(len(colorspace)):
        if colorspace[i].isnumeric():
            bpprgba.append(int(colorspace[i]))
        else:
            colorOrder += colorspace[i]
            
    for i in range(len(bpprgba) - 4):
        bpprgba.append(0)
        
    bytesPerPixel = round(sum(bpprgba) / 8)
    # print(colorspace, bytesPerPixel, colorOrder, bpprgba)
    
    if endian == 'big' or endian == 1:
        colorOrder = colorOrder[::-1]
        # bpprgba = bpprgba[::-1] # don't know whether to use this or not
    
    with open(path, 'rb') as file:
        return WrapRawData(file.read(), size[0], size[1], bytesPerPixel, bpprgba[0], bpprgba[1], bpprgba[2], bpprgba[3], colorOrder, premultiplyAlpha, dePremultiplyAlpha, offset)

def WrapRawData(rawData : bytes, width : int, height : int, bytesPerPixel : int, redBits : int, greenBits : int, blueBits : int, alphaBits : int, colorOrder : str, premultiplyAlpha : bool = False, dePremultiplyAlpha : bool = False, offset : int = 0):
    _8BIT_MASK = 256.0
    OUTBITDEPTH = 8
    DEBUG_MODE = False
    
    colorOrder = colorOrder.lower()
    
    # width and height are switched due to how PIL creates an image from array
    # image = [[(0, 0, 0, 0)] * height] * width
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    x = 0
    y = 0
    
    redMask = GenerateBinaryMask(redBits)
    greenMask = GenerateBinaryMask(greenBits)
    blueMask = GenerateBinaryMask(blueBits)
    alphaMask = GenerateBinaryMask(alphaBits)
    
    redMax = math.pow(2, redBits)
    greenMax = math.pow(2, greenBits)
    blueMax = math.pow(2, blueBits)
    alphaMax = math.pow(2, alphaBits)
    
    # determine number of loops needed to get every pixel
    numLoops = int(len(rawData) / bytesPerPixel)
    
    # loop for each set of bytes (one pixel)
    for i in range(numLoops):
        pixel = 0
        
        # read all bytes for this pixel
        for j in range(bytesPerPixel):
            nextByte = rawData[i * bytesPerPixel + j + offset]
            
            # print(f'Read byte: {hex(nextByte)}')
            
            # move the byte up
            # if (reverseBytes)
            nextByte = nextByte << (8 * j)
            # else
            # pixel = pixel << 8
            
            # append the next one
            pixel += nextByte
            # print(f'Pixel is now: {hex(pixel)}')
            
        # print(f'Pixel: {pixel}')
        
        # get RGBA values from the pixel
        r, g, b, a, = 0, 0, 0, 0
        
        # loop for each channel
        for j in reversed(range(len(colorOrder))):
            color = colorOrder[j]
            
            if color == 'r':
                r = pixel & redMask
                pixel = pixel >> redBits
                
            elif color == 'g':
                g = pixel & greenMask
                pixel = pixel >> greenBits
            
            elif color == 'b':
                b = pixel & blueMask
                pixel = pixel >> blueBits
                
            else:
                a = pixel & alphaMask
                pixel = pixel >> alphaBits
                
        # print(f'Before scale:\nR: {r} G: {g} B: {b} A: {a}')
        
        # scale colors to 8-bit depth (not sure which method is better)
        
        # via floating point division
        if (redMax > 1):
            r = round(r * ((_8BIT_MASK - 1) / (redMax - 1)))
        if (greenMax > 1):
            g = round(g * ((_8BIT_MASK - 1) / (greenMax - 1)))
        if (blueMax > 1):
            b = round(b * ((_8BIT_MASK - 1) / (blueMax - 1)))
        if (alphaMax > 1):
            a = round(a * ((_8BIT_MASK - 1) / (alphaMax - 1)))
        
        # via bit shifting
        # rShift = OUTBITDEPTH - redBits
        # gShift = OUTBITDEPTH - greenBits
        # bShift = OUTBITDEPTH - blueBits
        # aShift = OUTBITDEPTH - alphaBits
        # r = (r << rShift) + (r >> (redBits - rShift))
        # g = (g << gShift) + (r >> (greenBits - gShift))
        # b = (b << bShift) + (r >> (blueBits - bShift))
        # a = (a << aShift) + (a >> (alphaBits - aShift))
        
        # print(f'After scale:\nR: {r} G: {g} B: {b} A: {a}')
        
        # if there are no bits allotted for an alpha channel, make pixel opaque rather than invisible
        if alphaBits == 0:
            a = 255
            
        # a = 255
            
        if dePremultiplyAlpha:
            r = round(r * a / 255.0)
            g = round(g * a / 255.0)
            b = round(b * a / 255.0)
            
        if premultiplyAlpha:
            if (a != 0):
                r = round(r * 255.0 / a)
                g = round(g * 255.0 / a)
                b = round(b * 255.0 / a)
            
        # set the pixel
        rgba = (int(r), int(g), int(b), int(a))
        # print(rgba)
        # image[x][y] = rgba
        image.putpixel((x,y), rgba)
        
        # break after first pixel if in debug mode
        
        
        # iterate coordinates
        x += 1
        if (x == width):
            x = 0
            y += 1
            # if (y > (height - 300) or y % 100 == 0):
            #     print(f'Line {y} of {height} done')
            #     if (DEBUG_MODE):
            #         break
                
        # if there's extra data (like the door overlays in the lawns), stop once the height is reached
        if y == height:
            break
        
    
    return image

def GenerateBinaryMask(numOnes):
    binaryMask = 0
    for i in range(numOnes):
        binaryMask *= 2
        binaryMask += 1
        
    return binaryMask

# Example usage:
root = Tk()
root.withdraw()
path = tkinter.filedialog.askopenfilename(filetypes =[('WALTEX', '*.waltex'),('All Files', '*.*')],
                                        title='Select Waltex File to use')
output_name = path.split('.')[0] + '.png'

with open(path, "rb") as f:
    rawdata = f.read()
if rawdata[:4].decode("utf-8") != "WALT":
    raise ValueError("Not a valid WALTex file")
tex_fmt = rawdata[5]
tex_size = rawdata[7]
#Find what waltex format it is
if tex_fmt == 0x0:
    print('rgba8888 format detected.')
    rawcolor = 'abgr8888'
    offset = 16
    width = int.from_bytes(rawdata[6:8], "little")
    height = int.from_bytes(rawdata[8:10], "little")
elif tex_fmt == 0x3:
    rawcolor = 'rgba4444'
    offset = 16
    #Some rgba4444s have width and height flipped, this byte seems to be the answer
    if tex_size == 0x3:
        print('rgba4444 format detected. Flipped dimensions.')
        height = int.from_bytes(rawdata[6:8], "little")
        width = int.from_bytes(rawdata[8:10], "little")
    #Normal version
    #elif tex_size == 0x1 or tex_size == 0x2 or tex_size == 0x4 or tex_size == 0x5 or tex_size == 0x6 or tex_size == 0x8 or tex_size == 0x10:
    else:
        print('rgba4444 format detected.')
        width = int.from_bytes(rawdata[6:8], "little")
        height = int.from_bytes(rawdata[8:10], "little")
    #Otherwise I don't know
    #else: Prior to with "width fixing" (below) we had to do this
    #    print('rgba4444 format detected. Unknown dimensions.')
    #    width = int(input("Please enter width here: "))
    #    height = int(input("Please enter height here: "))
else:
    raise ValueError("Unknown texture format")
    
#Some textures are dumb and have weird widths. This seems to occur with textures that only have a single sprite.
if (width != 32 and width != 64 and width != 128 and width != 256 and width != 512 and width != 1024 and width != 2048 and width != 4096):
            print("Unusual width detected. Adjusting automatically!")
            if (width < 32):
                width = 32
            if (width > 32 and width < 64):
                width = 64
            if (width > 64 and width < 128):
                width = 128
            if (width > 128 and width < 256):
                width = 256
            if (width > 256 and width < 512):
                width = 512
            if (width > 512 and width < 1024):
                width = 1024
            if (width > 1024 and width < 2048):
                width = 2048
            if (width > 2048):
                width = 4096
    
print(f"Processing {(os.path.basename(path))}...")

image = WaltexImage(path, (width, height), rawcolor, 'false', 'false', 'little', offset)
#Download as PNG
output_dir = "out"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
image.save('out/' + os.path.splitext(os.path.basename(output_name + ".png"))[0], "PNG")
print(f"Saved as {(os.path.basename(output_name))}")
