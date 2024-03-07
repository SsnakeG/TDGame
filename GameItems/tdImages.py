from pygame import mixer, image, transform

FPS = 60
block_size = 25

mixer.init()

path = __file__
path_len = len(path)-12
path = path[0:path_len]

imgsPath = f"{path}/imgs/"
audioPath = f"{path}/audio/"

# audio
# bongSong = mixer.Sound(f"{audioPath}TacoBellBong.mp3")

# audios = [bongSong]

audioList = []

# troop selection section
selector = image.load(f'{imgsPath}Selection_box.png')
scout_img = image.load(f'{imgsPath}towers/Scout.png')
rifleMan_img = image.load(f'{imgsPath}towers/RifleMan.png')
minigunner_img = image.load(f'{imgsPath}towers/Minigunner.png')
sniper_img = image.load(f'{imgsPath}towers/Sniper.png')
sniper_img = transform.rotate(sniper_img, 90)
turret_img = image.load(f'{imgsPath}towers/Turret.png')
pyro_img = image.load(f'{imgsPath}towers/Pyro.png')
freezer_img = image.load(f'{imgsPath}towers/Freezer.png')
demoMan_img = image.load(f'{imgsPath}towers/Demo-man.png')

farm_img = image.load(f'{imgsPath}towers/Farm.png')

# upgrades (range, damage, speed, price, image, (SPECIAL))
scout_upgrades = [(1, 1, 0, 100, image.load(f'{imgsPath}towers/Scout1.png')),
                  (0, 1, 0.25, 250, image.load(f'{imgsPath}towers/Scout2.png')),
                  (2, 1, 0, 375, image.load(f'{imgsPath}towers/Scout3.png')),
                  (2, 0, 0.25, 500, image.load(f'{imgsPath}towers/Scout4.png'))]
sniper_upgrades = [(1, 2, 0, 350, transform.rotate(image.load(f'{imgsPath}towers/Sniper1.png'), 90)),
                   (1, 2, 0.25, 650, transform.rotate(image.load(f'{imgsPath}towers/Sniper2.png'), 90)),
                   (1, 2, 0.25, 1000, transform.rotate(image.load(f'{imgsPath}towers/Sniper3.png'), 90)),
                   (2, 9, 0, 1500, transform.rotate(image.load(f'{imgsPath}towers/Sniper4.png'), 90))]
rifle_man_upgrades = [(1, 1, 0, 450, image.load(f'{imgsPath}towers/RifleMan1.png')),
                      (0, 1, 0, 550, image.load(f'{imgsPath}towers/RifleMan2.png')),
                      (2, 0, 0.1, 750, image.load(f'{imgsPath}towers/RifleMan3.png')),
                      (1, 2, 0, 1000, image.load(f'{imgsPath}towers/RifleMan4.png'))]
minigunner_upgrades = [(0, 1, 0, 450, image.load(f'{imgsPath}towers/Minigunner1.png')),
                       (0, 1, 0, 800, image.load(f'{imgsPath}towers/Minigunner2.png')),
                       (1, 1, 0.1, 1000, image.load(f'{imgsPath}towers/Minigunner3.png')),
                       (1, 1, 0, 1500, image.load(f'{imgsPath}towers/Minigunner4.png'))]
turret_upgrades = [(2, 1, 0, 1500, image.load(f'{imgsPath}towers/Turret1.png')),
                   (-1, 1, 0.5, 2000, image.load(f'{imgsPath}towers/Turret2.png')),
                   (2, 4, 0.25, 5500, image.load(f'{imgsPath}towers/Turret3.png')),
                   (2, 2, 0.15, 10000, image.load(f'{imgsPath}towers/Turret4.png'))]
super_soldier_upgrades = [(0, 100, .5, 50, image.load(f'{imgsPath}towers/Scout1.png')),
                          (0, 100, .5, 150, image.load(f'{imgsPath}towers/Scout2.png')),
                          (0, 100, .5, 750, image.load(f'{imgsPath}towers/Scout3.png')),
                          (0, 100, .5, 1150, image.load(f'{imgsPath}towers/Scout4.png'))]
pyro_upgrades = [(1, 1, 0, 550, image.load(f'{imgsPath}towers/Pyro1.png'), (1, 3 * FPS)),
                 (1, 2, 0.5, 900, image.load(f'{imgsPath}towers/Pyro2.png'), (2, 4 * FPS)),
                 (1, 1, 0, 1250, image.load(f'{imgsPath}towers/Pyro3.png'), (2, 5 * FPS)),
                 (1, 3, 0.5, 1750, image.load(f'{imgsPath}towers/Pyro4.png'), (3, 5 * FPS))]
freezer_upgrades = [(1, 0, 0, 300, image.load(f'{imgsPath}towers/Freezer1.png'), (0.35, 3 * FPS)),
                    (1, 2, 0.75, 650, image.load(f'{imgsPath}towers/Freezer2.png'), (0.35, 4 * FPS)),
                    (1, 1, 0, 900, image.load(f'{imgsPath}towers/Freezer3.png'), (0.5, 5 * FPS)),
                    (1, 3, 0.25, 1100, image.load(f'{imgsPath}towers/Freezer4.png'), (0.6, 5 * FPS))]
demoMan_upgrades = [(0, 1, 0, 200, image.load(f'{imgsPath}towers/Demo-man1.png'), (2, 2)),
                    (1, 2, 0, 500, image.load(f'{imgsPath}towers/Demo-man2.png'), (3, 4)),
                    (0, 1, 0.5, 650, image.load(f'{imgsPath}towers/Demo-man3.png'), (3, 5)),
                    (2, 5, 0.5, 1250, image.load(f'{imgsPath}towers/Demo-man4.png'), (3, 8))]
# money gain per wave, price, image
farm_upgrades = [(250, 500, image.load(f'{imgsPath}towers/Farm1.png')),
                 (450, 950, image.load(f'{imgsPath}towers/Farm2.png')),
                 (750, 2150, image.load(f'{imgsPath}towers/Farm3.png')),
                 (1000, 4500, image.load(f'{imgsPath}towers/Farm4.png'))]

# towers stats (damage, range, speed, image, cost, upgrades, name)
# pyro special : (damage, duration(seconds))
# ice special : (speed reduction, duration(seconds))
# demo special : (explosion range, explosion damage)
scoutStats = [1, 4, 0.75, scout_img, 100, scout_upgrades, 'Scout']
sniper_stats = [5, 10, 1.5, sniper_img, 250, sniper_upgrades, 'Sniper']
rifle_man_stats = [1, 4, 0.3, rifleMan_img, 250, rifle_man_upgrades, 'Rifle']
minigunner_stats = [1, 6, 0.2, minigunner_img, 750, minigunner_upgrades, 'Minigunner']
turret_stats = [4, 8, 1, turret_img, 2500, turret_upgrades, 'Turret']
pyro_stats = [1, 6, 1.5, pyro_img, 650, pyro_upgrades, 'Pyromaniac', (1, 2 * FPS)]
freezer_stats = [2, 5, 1.5, freezer_img, 450, freezer_upgrades, 'Freezer', (0.25, 2 * FPS)]
demoMan_stats = [3, 5, 2, demoMan_img, 450, demoMan_upgrades, 'Demolition', (1, 2)]
super_soldier_stats = [100, 20, 2.1, scout_img, 50, super_soldier_upgrades, '']

farm_stats = [100, 250, farm_img, farm_upgrades, "Farm"]

# enemy images
normal_img = image.load(f'{imgsPath}enemies/Normal.png')
slow_img = image.load(f'{imgsPath}enemies/Slow.png')
fast_img = image.load(f'{imgsPath}enemies/Fast.png')
tank_img = image.load(f'{imgsPath}enemies/Tank.png')
boss_img = image.load(f'{imgsPath}enemies/Boss.png')
slow_boss_img = image.load(f'{imgsPath}enemies/Slow_Boss.png')
fast_boss_img = image.load(f'{imgsPath}enemies/Fast_Boss.png')
tank_boss_img = image.load(f'{imgsPath}enemies/Tank_Boss.png')
final_boss_img = image.load(f'{imgsPath}enemies/Final_Boss.png')

fireImg = image.load(f'{imgsPath}Fire.png')
iceImg = image.load(f'{imgsPath}Ice.png')

# speed variables
REG_SLOW = 0.5
REG_SPEED = 1
REG_FAST = 3

BOSS_SLOW = 0.25
BOSS_SPEED = 0.5
BOSS_FAST = 2
FINAL_BOSS = 0.1

# character image, health, movement speed, character size
enemyStats = {"Normal": [normal_img, 10, REG_SPEED, block_size],
              "Slow": [slow_img, 30, REG_SLOW, block_size],
              "Fast": [fast_img, 15, REG_FAST, block_size],
              "Tank": [tank_img, 750, REG_SLOW, block_size],
              "Boss": [boss_img, 100, BOSS_SPEED, block_size],
              "Slow Boss": [slow_boss_img, 2000, BOSS_SLOW, block_size],
              "Fast Boss": [fast_boss_img, 3000, BOSS_FAST, block_size],
              "Tank Boss": [tank_boss_img, 35000, BOSS_SLOW, block_size],
              "Final Boss": [final_boss_img, 1000000, FINAL_BOSS, block_size]}


background = image.load(f'{imgsPath}Background.png')
playImg = image.load(f'{imgsPath}Playimg.png')
optionsImg = image.load(f'{imgsPath}Optionsimg.png')
quitImg = image.load(f'{imgsPath}Quitimg.png')
newMapImg = image.load(f'{imgsPath}Newmapimg.png')
leftArrow = image.load(f'{imgsPath}LeftArrow.png')
rightArrow = image.load(f'{imgsPath}RightArrow.png')
menuImg = image.load(f'{imgsPath}Mainmenuimg.png')
loadOutImg = image.load(f'{imgsPath}Loadoutimg.png')
undoImg = image.load(f'{imgsPath}UndoImg.png')
RedoImg = image.load(f'{imgsPath}RedoImg.png')
saveImg = image.load(f'{imgsPath}saveIcon.png')
trashImg = image.load(f'{imgsPath}trashIcon.png')
homeImg = image.load(f'{imgsPath}homeIcon.png')
mapSelected = transform.scale(image.load(f'{imgsPath}mapSelector.png'), (120, 120))
popupBackground = image.load(f'{imgsPath}BlankImg.png')

checkImg = image.load(f'{imgsPath}Check.png')
xImg = image.load(f'{imgsPath}Ex.png')

