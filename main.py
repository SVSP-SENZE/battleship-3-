import pygame
import random
from shipnew import SHIP_TYPES_LIST, SHIP_SIZES, update_ship_status_on_hit, reset_ship_status, create_ship_record
from boardnew import can_place, place_ship, auto_place_with_records, check_win
from gamemanager import process_attack
import filemanager

pygame.init()
scr = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("BATTLESHIP")
clk = pygame.time.Clock()

# fonts
f1 = pygame.font.Font(None, 50)
f2 = pygame.font.Font(None, 30)

# input ui
inpbox = pygame.Rect(350, 350, 300, 60)
inpactive = False
inptext = ""
p1 = ""
p2 = ""
namecur = "p1"

# background image (pls work and not break on teacher's pc)
try:
    bgimg = pygame.image.load(r"C:\Users\srika\OneDrive\Desktop\random.jpg").convert()
    bgimg = pygame.transform.scale(bgimg, (1000, 800))
except Exception:
    # silly comment 1
    bgimg = pygame.Surface((1000, 800))
    bgimg.fill((20, 50, 80))  # fallback bg, vibes of sadness

# ship placeholder
try:
    shipimg = pygame.image.load(r"C:\Users\srika\OneDrive\Desktop\ship.jpg").convert_alpha()
    shipimg = pygame.transform.scale(shipimg, (35, 35))
except Exception:
    # silly comment 2
    shipimg = pygame.Surface((35, 35), pygame.SRCALPHA)
    pygame.draw.circle(shipimg, (200, 200, 200), (17, 17), 15)  # simple circle ship lol (budget Titanic)

# buttons
btnmanual = pygame.Rect(300, 300, 400, 80)
btnauto = pygame.Rect(300, 420, 400, 80)
btnresume = pygame.Rect(300, 540, 400, 60)
btnrestart = pygame.Rect(720, 50, 250, 40)

# game state
gs = "input"
grd = 10
brdtl = (300, 200)
shipsplaced = 0

# boards and attempts
p1br = [[0] * grd for _ in range(grd)]
p2br = [[0] * grd for _ in range(grd)]
p1att = [[0] * grd for _ in range(grd)]
p2att = [[0] * grd for _ in range(grd)]

curply = "p1"
winner = None

# colors
WHITE = (255, 255, 255)
GRAY  = (150, 150, 150)
RED   = (220, 50, 50)
BLUE  = (50, 120, 220)

# placement
shipidx = 0
shipdir = "H"

# ship records
p1ships = []
p2ships = []
ssp1 = {name: False for name, _ in SHIP_TYPES_LIST}
ssp2 = {name: False for name, _ in SHIP_TYPES_LIST}

hassave = filemanager.has_save()

# little timers
attack_result = ""
result_timer = 0
placement_timer = 0
last_attacker = None
current_turn_player = ""

# ---------- SAVE LOAD ----------
def makesave():
    # silly comment 3: saving everything like hoarding memes
    return {
        "gs": gs,
        "grd": grd,
        "brdtl": brdtl,
        "p1br": p1br,
        "p2br": p2br,
        "p1att": p1att,
        "p2att": p2att,
        "curply": curply,
        "winner": winner,
        "shipidx": shipidx,
        "shipdir": shipdir,
        "shipsplaced": shipsplaced,
        "p1ships": p1ships,
        "p2ships": p2ships,
        "ssp1": ssp1,
        "ssp2": ssp2,
        "p1": p1,
        "p2": p2,
        "attack_result": attack_result,
        "last_attacker": last_attacker,
        "current_turn_player": current_turn_player
    }

def loadsave(s):
    # silly comment 4: hopefully nothing explodes
    global gs, grd, brdtl
    global p1br, p2br, p1att, p2att
    global curply, winner
    global shipidx, shipdir, shipsplaced
    global p1ships, p2ships, ssp1, ssp2
    global p1, p2, attack_result, last_attacker, current_turn_player

    if not s:
        return False
    gs = s.get("gs", gs)
    grd = s.get("grd", grd)
    brdtl = s.get("brdtl", brdtl)
    p1br = s.get("p1br", p1br)
    p2br = s.get("p2br", p2br)
    p1att = s.get("p1att", p1att)
    p2att = s.get("p2att", p2att)
    curply = s.get("curply", curply)
    winner = s.get("winner", winner)
    shipidx = s.get("shipidx", shipidx)
    shipdir = s.get("shipdir", shipdir)
    shipsplaced = s.get("shipsplaced", shipsplaced)
    p1ships = s.get("p1ships", p1ships)
    p2ships = s.get("p2ships", p2ships)
    ssp1 = s.get("ssp1", ssp1)
    ssp2 = s.get("ssp2", ssp2)
    p1 = s.get("p1", p1)
    p2 = s.get("p2", p2)
    attack_result = s.get("attack_result", attack_result)
    last_attacker = s.get("last_attacker", last_attacker)
    current_turn_player = s.get("current_turn_player", current_turn_player)
    return True

# ---------- DRAW HELPERS ----------
def drawboard(bd, top_left):
    for r in range(grd):
        for c in range(grd):
            rect = pygame.Rect(top_left[0] + c * 35, top_left[1] + r * 35, 35, 35)
            pygame.draw.rect(scr, WHITE, rect, 2)
            if bd[r][c] == 1:
                scr.blit(shipimg, rect.topleft)

def drawattempts(at, top_left):
    for r in range(grd):
        for c in range(grd):
            rect = pygame.Rect(top_left[0] + c * 35, top_left[1] + r * 35, 35, 35)
            if at[r][c] == 2:
                pygame.draw.rect(scr, RED, rect)
            elif at[r][c] == 3:
                pygame.draw.rect(scr, BLUE, rect)
            pygame.draw.rect(scr, GRAY, rect, 1)

def drawfull(board, attempts, top_left):
    for r in range(grd):
        for c in range(grd):
            rect = pygame.Rect(top_left[0] + c * 35, top_left[1] + r * 35, 35, 35)
            pygame.draw.rect(scr, (40,40,40), rect)
            if board[r][c] == 1:
                scr.blit(shipimg, rect.topleft)
            if attempts[r][c] == 2:
                pygame.draw.rect(scr, RED, rect)
            elif attempts[r][c] == 3:
                pygame.draw.rect(scr, BLUE, rect)
            pygame.draw.rect(scr, WHITE, rect, 1)

def drawshipstatus(status, pos=(700,200)):
    x,y = pos
    scr.blit(f1.render("SHIPS", True, (255,255,0)), (x,y))
    y += 60
    for name, size in SHIP_TYPES_LIST:
        col = RED if status.get(name, False) else WHITE
        scr.blit(f2.render(f"{size} - {name}", True, col), (x,y))
        y += 40

# ---------- MAIN LOOP ----------
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            try:
                filemanager.save_game(makesave())  # silly comment 5: saving like it's the last second of Jenga
            except Exception:
                pass
            run = False

        # rotate ship key & save (because why not)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                shipdir = "V" if shipdir == "H" else "H"
            if event.key == pygame.K_s:
                try:
                    filemanager.save_game(makesave())
                    # silly comment 6: ctrl+s muscle memory activated
                except Exception:
                    print("save failed lol")

        # ---------- NAME INPUT ----------
        if gs == "input":
            if event.type == pygame.MOUSEBUTTONDOWN:
                inpactive = inpbox.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and inpactive:
                if event.key == pygame.K_RETURN:
                    if inptext.strip() != "":
                        if namecur == "p1":
                            p1 = inptext.strip()
                            inptext = ""
                            namecur = "p2"
                        elif namecur == "p2":
                            p2 = inptext.strip()
                            inptext = ""
                            namecur = "done"
                            inpactive = False
                elif event.key == pygame.K_BACKSPACE:
                    inptext = inptext[:-1]
                else:
                    if len(inptext) < 20:
                        inptext += event.unicode
            if event.type == pygame.KEYDOWN and namecur == "done":
                if event.key == pygame.K_SPACE:
                    gs = "menu"

        # ---------- MENU ----------
        elif gs == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btnmanual.collidepoint(event.pos):
                    # silly comment 7: manual mode = pain mode
                    p1ships.clear(); p2ships.clear()
                    p1br = [[0]*grd for _ in range(grd)]
                    p2br = [[0]*grd for _ in range(grd)]
                    p1att = [[0]*grd for _ in range(grd)]
                    p2att = [[0]*grd for _ in range(grd)]
                    reset_ship_status(ssp1); reset_ship_status(ssp2)
                    shipidx = 0; shipdir = "H"
                    gs = "setupmanualp1"
                elif btnauto.collidepoint(event.pos):
                    # silly comment 8: AI placing ships better than humans
                    p1ships.clear(); p2ships.clear()
                    p1br = [[0]*grd for _ in range(grd)]
                    p2br = [[0]*grd for _ in range(grd)]
                    p1att = [[0]*grd for _ in range(grd)]
                    p2att = [[0]*grd for _ in range(grd)]
                    reset_ship_status(ssp1); reset_ship_status(ssp2)
                    auto_place_with_records(p1br, p1ships, grd)
                    auto_place_with_records(p2br, p2ships, grd)
                    gs = "ready"
                elif btnresume.collidepoint(event.pos) and hassave:
                    # silly comment 9: time travel using saved data
                    try:
                        data = filemanager.load_game()
                        if data: loadsave(data)
                    except Exception: pass

        # ---------- MANUAL P1 SHIP PLACEMENT ----------
        elif gs == "setupmanualp1":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                gx = (x - brdtl[0]) // 35
                gy = (y - brdtl[1]) // 35
                if 0 <= gx < grd and 0 <= gy < grd:
                    if shipidx < len(SHIP_SIZES):
                        size = SHIP_SIZES[shipidx]
                        if can_place(p1br, gy, gx, size, shipdir, grd):
                            cells = place_ship(p1br, gy, gx, size, shipdir)
                            nm = SHIP_TYPES_LIST[shipidx][0]
                            p1ships.append(create_ship_record(nm, cells))
                            shipidx += 1
                    if shipidx >= len(SHIP_SIZES):
                        shipidx = 0; shipdir = "H"
                        placement_timer = pygame.time.get_ticks() + 500
                        gs = "placement_showboard_p1"

        # ---------- MANUAL P2 SHIP PLACEMENT ----------
        elif gs == "setupmanualp2":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                gx = (x - brdtl[0]) // 35
                gy = (y - brdtl[1]) // 35
                if 0 <= gx < grd and 0 <= gy < grd:
                    if shipidx < len(SHIP_SIZES):
                        size = SHIP_SIZES[shipidx]
                        if can_place(p2br, gy, gx, size, shipdir, grd):
                            cells = place_ship(p2br, gy, gx, size, shipdir)
                            nm = SHIP_TYPES_LIST[shipidx][0]
                            p2ships.append(create_ship_record(nm, cells))
                            shipidx += 1
                    if shipidx >= len(SHIP_SIZES):
                        shipidx = 0; shipdir = "H"
                        placement_timer = pygame.time.get_ticks() + 500
                        gs = "placement_showboard_p2"

        elif gs == "placement_showboard_p1":
            if pygame.time.get_ticks() >= placement_timer:
                placement_timer = pygame.time.get_ticks() + 500
                gs = "placement_done_p1"

        elif gs == "placement_done_p1":
            if pygame.time.get_ticks() >= placement_timer:
                shipidx = 0; shipdir = "H"
                gs = "setupmanualp2"

        elif gs == "placement_showboard_p2":
            if pygame.time.get_ticks() >= placement_timer:
                placement_timer = pygame.time.get_ticks() + 500
                gs = "placement_done_p2"

        elif gs == "placement_done_p2":
            if pygame.time.get_ticks() >= placement_timer:
                shipidx = 0; shipdir = "H"
                gs = "ready"

        # ---------- READY ----------
        elif gs == "ready":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                curply = "p1"
                gs = "battle"

        # ---------- BATTLE ----------
        elif gs == "battle":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                gx = (x - brdtl[0]) // 35
                gy = (y - brdtl[1]) // 35
                if 0 <= gx < grd and 0 <= gy < grd:
                    prev = curply
                    last_attacker = prev
                    curply, winner = process_attack(
                        curply, gy, gx,
                        p1br, p2br,
                        p1att, p2att,
                        p1ships, p2ships,
                        ssp1, ssp2,
                        p1, p2, grd
                    )
                    # switching turns like tossing hot potato
                    curply = "p2" if prev == "p1" else "p1"
                    try: filemanager.save_game(makesave())
                    except: pass
                    if winner is not None:
                        gs = "gameover"
                    else:
                        if prev == "p1":
                            was_hit = (p2att[gy][gx] == 2)
                        else:
                            was_hit = (p1att[gy][gx] == 2)
                        attack_result = "HIT!" if was_hit else "MISS!"
                        #  dramatic pause for effect
                        result_timer = pygame.time.get_ticks() + 500
                        gs = "show_result"

        elif gs == "show_result":
            if pygame.time.get_ticks() >= result_timer:
                current_turn_player = p1 if curply == "p1" else p2
                gs = "switch"

        elif gs == "switch":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # hiding screen like cheating in exams
                gs = "battle"

        elif gs == "gameover":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # silly comment 13: exiting like rage quit but happier
                run = False

        # restart anytime (almost…)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btnrestart.collidepoint(event.pos):
                #  deleting history like clearing browser tabs fast
                gs = "menu"
                p1ships.clear(); p2ships.clear()
                p1br = [[0]*grd for _ in range(grd)]
                p2br = [[0]*grd for _ in range(grd)]
                p1att = [[0]*grd for _ in range(grd)]
                p2att = [[0]*grd for _ in range(grd)]
                reset_ship_status(ssp1); reset_ship_status(ssp2)

    # ---------- DRAW SECTION ----------
    scr.blit(bgimg, (0,0))

    if gs == "input":
        if namecur == "p1":
            scr.blit(f1.render("Enter p1:", True, WHITE), (250, 200))
        elif namecur == "p2":
            scr.blit(f1.render("Enter p2:", True, WHITE), (250, 200))
        else:
            scr.blit(f1.render(f"Welcome {p1} & {p2}!", True, WHITE), (200, 300))
            scr.blit(f2.render("Press SPACE to start the game!", True, (255, 200, 0)), (250, 380))
            pygame.display.flip()
            clk.tick(60)
            continue
        pygame.draw.rect(scr, (200,0,0), inpbox, 5)
        scr.blit(f1.render(inptext, True, WHITE), (inpbox.x + 10, inpbox.y + 10))

    elif gs == "menu":
        scr.blit(f1.render("Choose set up mode", True, WHITE), (250, 250))
        pygame.draw.rect(scr, (30, 120, 200), btnmanual)
        pygame.draw.rect(scr, (30, 120, 200), btnauto)
        scr.blit(f2.render("Set board manually", True, WHITE), (btnmanual.x + 50, btnmanual.y + 35))
        scr.blit(f2.render("Automatic setup", True, WHITE), (btnauto.x + 35, btnauto.y + 45))
        if hassave:
            pygame.draw.rect(scr, (40, 180, 100), btnresume)
            scr.blit(f2.render("Resume saved game", True, WHITE), (btnresume.x + 60, btnresume.y + 20))

    elif gs == "setupmanualp1":
        scr.blit(f2.render(f"{p1} place ships", True, WHITE), (300, 100))
        drawboard(p1br, brdtl)
        drawshipstatus(ssp1)

    elif gs == "setupmanualp2":
        scr.blit(f2.render(f"{p2} place ships", True, WHITE), (300, 100))
        drawboard(p2br, brdtl)
        drawshipstatus(ssp2)

    elif gs == "placement_showboard_p1":
        scr.blit(bgimg, (0,0))
        drawboard(p1br, brdtl)
        scr.blit(f2.render("Final ship placed!", True, WHITE), (360,150))

    elif gs == "placement_done_p1":
        scr.blit(bgimg, (0,0))
        drawboard(p1br, brdtl)
        scr.blit(f1.render(f"{p1} DONE!", True, WHITE), (400,600))

    elif gs == "placement_showboard_p2":
        scr.blit(bgimg, (0,0))
        drawboard(p2br, brdtl)
        scr.blit(f2.render("Final ship placed!", True, WHITE), (360,150))

    elif gs == "placement_done_p2":
        scr.blit(bgimg, (0,0))
        drawboard(p2br, brdtl)
        scr.blit(f1.render(f"{p2} DONE!", True, WHITE), (400,600))

    elif gs == "ready":
        scr.blit(f1.render("Both players ready!", True, (0,200,0)), (250,300))
        scr.blit(f2.render("Press SPACE to start the battle!", True, WHITE), (300,380))

    elif gs == "battle":
        scr.blit(f1.render(f"{p1 if curply=='p1' else p2}'s turn", True, (255,220,0)), (300, 130))
        scr.blit(f2.render("Click grid to attack!", True, WHITE), (320, 170))
        if curply == "p1":
            drawattempts(p2att, brdtl)
            drawshipstatus(ssp2)
        else:
            drawattempts(p1att, brdtl)
            drawshipstatus(ssp1)

    elif gs == "show_result":
        scr.blit(bgimg, (0,0))
        if last_attacker == "p1":
            drawfull(p1br, p1att, brdtl)
            drawattempts(p2att, brdtl)
            drawshipstatus(ssp2)
        else:
            drawfull(p2br, p2att, brdtl)
            drawattempts(p1att, brdtl)
            drawshipstatus(ssp1)
        col = RED if attack_result == "HIT!" else BLUE
        scr.blit(f1.render(attack_result, True, col), (430, 580))
        scr.blit(f2.render("Press SPACE to continue", True, (255,255,0)), (380, 620))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            current_turn_player = p1 if curply == "p1" else p2
            gs = "switch"

    elif gs == "switch":
        scr.blit(f1.render(f"{current_turn_player}'s turn!", True, WHITE), (300,320))
        scr.blit(f2.render("Press SPACE to continue", True, (255,255,0)), (320,380))

    elif gs == "gameover":
        scr.blit(f1.render(f"{winner} wins!", True, (0,200,0)), (330,300))
        scr.blit(f2.render("Press ESC to quit", True, WHITE), (370,370))

    # restart button (not shown in dramatic screens)
    if gs not in ("placement_showboard_p1", "placement_done_p1",
                  "placement_showboard_p2", "placement_done_p2",
                  "show_result"):
        pygame.draw.rect(scr, (100,100,100), btnrestart)
        scr.blit(f2.render("Restart (New Game)", True, WHITE), (btnrestart.x + 20, btnrestart.y + 8))

    pygame.display.flip()
    clk.tick(60)

pygame.quit()  # game over, time to touch grass
