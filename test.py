import identicon, sys, pygame, random
pygame.display.init()
pygame.font.init()

screen = pygame.display.set_mode([500,500])
font = pygame.font.SysFont('Arial', 16)

def makeRandomEthAddress():
    address = "0x"
    for i in range(40):
        address += random.choice(['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'])
    return address

def main():
    address = makeRandomEthAddress()
    icon = identicon.generateIdenticon(address, 300, 300)
    addrTextImage = font.render(address, False, (255,255,255))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    #generate a dummy address
                    address = makeRandomEthAddress()
                    icon = identicon.generateIdenticon(address, 300, 300)
                    addrTextImage = font.render(address, False, (255,255,255))
    
        screen.fill([0,0,0])
        screen.blit(icon, [100,100])
        screen.blit(addrTextImage, [100, 80])
        pygame.display.flip()

main()