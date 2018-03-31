import pygame
pygame.display.init()

def byteValToRangedVal(byteVal, rangeMin, rangeMax):
    rangeSize = rangeMax - rangeMin
    x = byteVal / 255.0
    
    return rangeMin + (rangeSize * x)

# def hexStrToByteList(hexStr):
    # assert(len(hexStr)%2 == 0)
    
    # onByte = 0
    # byteList = []
    # while onByte < len(hexStr)/2:
        # oneByteInHex = hexStr[onByte*2:(onByte+1)*2]
        # byteList.append(int(oneByteInHex, 16))
        # onByte += 1
    
    # return byteList

def hexToDec(hexStr):
    return int(hexStr, 16)

#Stores a hexString and allows consumption of a given number of 4-bit words
class consumableWordList:
    def __init__(self, hexStr):
        self.hexStr = hexStr
    
    def consumeWords(self, numWords):
        if (numWords > len(self.hexStr)):
            raise IndexError("ConsumableWordList has run out of data!")
        
        val = hexToDec(self.hexStr[:numWords])
        self.hexStr = self.hexStr[numWords:]
        return val
    
    def consumeWordsIntoRange(self, numWords, min, max):
        val = self.consumeWords(numWords)
        maxVal = 16**numWords - 1
        
        x = float(val) / maxVal
        
        rangeSize = max - min
        
        return (min + x*rangeSize)
    
    def wordsLeft(self):
        return len(self.hexStr)

def generateIdenticon(address, width, height):
    if (width%2 != 0):
        raise ValueError("Width must be divisible by 2")
    
    if (address[0:2] == "0x"):
        address = address[2:]
    if len(address) != 40:
        raise ValueError("Address is not the correct length!")
    
    dataSource = consumableWordList(address)
    #We now have 40 4-bit "word"s (one from each char in the Ethereum address), to use as a source to generate a face
    
    #We will generate half a face, then mirror it
    halfWidth = width/2
    halfFaceSurface = pygame.Surface((halfWidth, height), pygame.SRCALPHA, 32)
    #we will draw as if x=0 is the mirror line, and x>0 moves toward both edges.
    #y=0 will be the top edge, as in normal graphics code
    
    #halfFaceSurface.fill([0,0,0])
    #do we need to fill with a transparent layer? Not sure. Worry about it later.
    
    stringPos = 0 # where we are in the 
    
    #---face shape ([0:3])---
    
    #Choose a point each on bottom edge, side, and top edge.
    facePoints = [None, None, None]
    facePoints[0] = [dataSource.consumeWordsIntoRange(1, 0, halfWidth),    height]
    facePoints[2] = [dataSource.consumeWordsIntoRange(1, 0, halfWidth),    0]
    facePoints[1] = [halfWidth,                                            height-dataSource.consumeWordsIntoRange(1, 0, height)]
    
    cheekBoneHeight = facePoints[1][1] #For use later
    
    #---face color ([3:6])---
    #Hmm. Should we disallow a range of colors...? We won't for now, but perhaps will later.
    #Might also need to re-balance if the colors don't "look" different very often.
    #For now, we'll just use the byteVals directly.
    faceColor = [dataSource.consumeWordsIntoRange(1, 0, 255), dataSource.consumeWordsIntoRange(1, 0, 255), dataSource.consumeWordsIntoRange(1, 0, 255)]
    
    #---draw face shape---
    #Draw a polygon with above points, plus top and bottom of centerline, using the chosen color.
    pygame.draw.polygon(halfFaceSurface, faceColor, [[0,height]] + facePoints + [[0,0]])
    
    #---eye shape/pos ([6:12])---
    #3 points, drawn above cheekBoneHeight, and on the inside of the line between facePoints[1] and facePoints[2]
    
    #---eye color ([12:15])
    
    #---mouth shape ([15:19])---
    #(15) length of middle, horizontal line "middle of mouth"
    #(16,17) x and y of "outer" part of mouth
    #(18) how "open" is the mouth?
    
    #---mouth color ([19:21])
    
    #Other ideas...
    #ears, eyebrows, nose, top of torso, wrinkles, hair, pupil, background
    #background color/pattern could be catchall for any unused words at the end
    
    faceSurface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    #Draw half-face and reflect to other side
    faceSurface.blit(halfFaceSurface, [halfWidth, 0])
    reflectedHalfFaceSurface = pygame.transform.flip(halfFaceSurface, True, False)
    faceSurface.blit(reflectedHalfFaceSurface, [0,0])
    
    return faceSurface