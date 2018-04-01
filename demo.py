import identicon, sys, pygame, random
pygame.display.init()
pygame.font.init()

screen = pygame.display.set_mode([1000,1000])
font = pygame.font.SysFont('Arial', 16)

def makeRandomEthAddress():
    address = "0x"
    for i in range(40):
        address += random.choice(['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'])
    print(address)
    return address

def main():
    makeNewAddresses = True
    while True:
        if makeNewAddresses:
            makeNewAddresses = False
            addresses = []
            icons = []
            for i in range(100):
                addresses.append(makeRandomEthAddress())
                icons.append(identicon.generateIdenticon(addresses[-1], 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    #generate a dummy address
                    makeNewAddresses = True
    
        screen.fill([0,0,0])
        for i in range(100):
            x = i%10
            y = (i-x)/10
            pos = [x*75 + 25, y*75 + 25]
            screen.blit(icons[i], pos)
        pygame.display.flip()

main()