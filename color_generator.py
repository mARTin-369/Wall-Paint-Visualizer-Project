from colorharmonies import *
import extcolors

def extractColors(filename):
    tolerance = 32
    limit = 24
    colors, pixel_count = extcolors.extract_from_path(filename, tolerance, limit)
    return colors

# def getColorCombination(rgbColor, harmony):
#     color = Color(rgbColor,"","")
#     match harmony:
#         case 'C':
#             return complementaryColor(color)
#         case 'T':
#             return triadicColor(color)
#         case 'S':
#             return splitComplementaryColor(color)
#         case 'T':
#             return tetradicColor(color)
#         case 'C':
#             return analogousColor(color)
#         case 'C':
#             return monochromaticColor(color)
#         case _:
#             return [color]

