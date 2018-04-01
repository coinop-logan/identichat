import pygame
pygame.display.init()

#def byteValToRangedVal(byteVal, rangeMin, rangeMax):
#    rangeSize = rangeMax - rangeMin
#    x = byteVal / 255.0
    
#    return rangeMin + (rangeSize * x)

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
    
    def consumeWordsIntoColor(self):
        return [self.consumeWordsIntoRange(1, 0, 255), self.consumeWordsIntoRange(1, 0, 255), self.consumeWordsIntoRange(1, 0, 255)]
    
    def wordsLeft(self):
        return len(self.hexStr)

def drawHorizontalLine(surface, color, y):
    pygame.draw.line(surface, color, [0,y], [1000,y])
    
def drawVerticalLine(surface, color, x):
    pygame.draw.line(surface, color, [x,0], [x,1000])
    
        
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
    faceColor = dataSource.consumeWordsIntoColor()
    
    #---draw face shape---
    #Draw a polygon with above points, plus top and bottom of centerline, using the chosen color.
    pygame.draw.polygon(halfFaceSurface, faceColor, [[0,height]] + facePoints + [[0,0]])
    
    #---eye shape/pos ([6:12])---
    #3 points, drawn above cheekBoneHeight, and on the inside of the line between facePoints[1] and facePoints[2]
    eyePoints = [None, None, None]
    for i in range(3):
        xRatio = dataSource.consumeWordsIntoRange(1, 0, 1)
        yRatio = dataSource.consumeWordsIntoRange(1, 0, 1)
        
        y = yRatio * facePoints[1][1]
        
        xLimit = facePoints[2][0] + (yRatio * (facePoints[1][0] - facePoints[2][0]))
        
        x = xRatio * xLimit
        
        eyePoints[i] = [x,y]
    
    #---eye color ([12:15])
    eyeColor = dataSource.consumeWordsIntoColor()
    
    #---draw eye shape---
    pygame.draw.polygon(halfFaceSurface, eyeColor, eyePoints)
    
    #---mouth shape/pos ([15:20])---
    
    #(15) horizontal positioning, between cheekBoneHeight and bottom
    mouthMiddleYRatio = dataSource.consumeWordsIntoRange(1, 0, 1)
    mouthMiddleY = cheekBoneHeight + (mouthMiddleYRatio * (height - facePoints[1][1]))
    #drawHorizontalLine(halfFaceSurface, [255,0,0], mouthMiddleY)
    
    #(16) length of middle mouth line, from centerline
    #Use mouthMiddleYRatio and facePoint[1] to determine face edge horizontally, then divide by two, to find max x of the mouthMiddle line.
    mouthMiddleXMax = (facePoints[0][0] + ((1-mouthMiddleYRatio) * (facePoints[1][0] - facePoints[0][0]))) / 2
    mouthMiddleX = dataSource.consumeWordsIntoRange(1, 0, mouthMiddleXMax)
    
    #(17,18) x and y of "outer" part of mouth
    mouthEndXRatio = dataSource.consumeWordsIntoRange(1, 0, 1)
    mouthEndX = mouthMiddleX + (mouthEndXRatio * (halfWidth - mouthMiddleX))
    #drawVerticalLine(halfFaceSurface, [255,0,0], mouthMiddleXMax)
    
    if mouthEndX > facePoints[0][0]:
        xRatioOnBottomFaceEdge = (mouthEndX - facePoints[0][0]) / (width - facePoints[0][0])
        mouthEndYMaxOverall = cheekBoneHeight + ((1 - xRatioOnBottomFaceEdge) * (height - cheekBoneHeight))
    else:
        mouthEndYMaxOverall = height
    
    mouthEndYMax = cheekBoneHeight + ((1 - mouthEndXRatio) * (mouthEndYMaxOverall - cheekBoneHeight))
    mouthEndY = dataSource.consumeWordsIntoRange(1, cheekBoneHeight, mouthEndYMax)
    
    #assemble mouth points into list
    mouthPoints = [[0,            mouthMiddleY],
                   [mouthMiddleX, mouthMiddleY],
                   [mouthEndX,    mouthEndY]]
    
    #---mouth color ([19:21])
    mouthColor = dataSource.consumeWordsIntoColor()
    
    #---draw mouth---
    pygame.draw.lines(halfFaceSurface, mouthColor, False, mouthPoints, 3)
    
    #Other ideas...
    #ears, eyebrows, nose, top of torso, wrinkles, hair, pupil, background
    #background color/pattern could be catchall for any unused words at the end
    
    faceSurface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    #Draw half-face and reflect to other side
    faceSurface.blit(halfFaceSurface, [halfWidth, 0])
    reflectedHalfFaceSurface = pygame.transform.flip(halfFaceSurface, True, False)
    faceSurface.blit(reflectedHalfFaceSurface, [0,0])
    
    return faceSurface