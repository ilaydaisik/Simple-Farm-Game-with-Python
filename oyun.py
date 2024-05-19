import pygame
import sys
import random
from PIL import Image

# Pygame başlatma
pygame.init()
pygame.mixer.init()

# Pencere ayarları
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("İlayda Oyun")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_RED = (255, 100, 100)
DARK_RED = (200, 0, 0)
FONT_COLOR = WHITE
HOVER_COLOR = BLACK

# Font ayarları
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Resim yükleme ve ölçeklendirme fonksiyonu
def load_and_scale_image(path, width, height):
    with open(path, "rb") as file:
        img = Image.open(file).convert("RGBA")
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        data = img.tobytes("raw", "RGBA")
        return pygame.image.fromstring(data, img.size, "RGBA")
    
# Arka plan resimlerini yükle ve ölçeklendir
background_images = {
    'menu': load_and_scale_image('menu.webp', screen_width, screen_height),
    'campsite': load_and_scale_image('campsite.webp', screen_width, screen_height),
    'healinghouse': load_and_scale_image('healinghouse.webp', screen_width, screen_height),
    'farm': load_and_scale_image('farm.webp', screen_width, screen_height),
    'tavern': load_and_scale_image('tavern.webp', screen_width, screen_height),
    'forest': load_and_scale_image('forest.webp', screen_width, screen_height),
    'fight': load_and_scale_image('fight.webp', screen_width, screen_height),
    'drink': load_and_scale_image('drink.webp', screen_width, screen_height),
    'usta': load_and_scale_image('usta.webp', screen_width, screen_height),
    'food': load_and_scale_image('food.webp', screen_width, screen_height),
    'levelup': load_and_scale_image('levelup.webp', screen_width, screen_height),
    'showstatus': load_and_scale_image('showstatus.webp', screen_width, screen_height),
    'collect': load_and_scale_image('collect.webp', screen_width, screen_height),
    'intro': load_and_scale_image('intro.webp', screen_width, screen_height)
}

# Karakter sınıfı
class Karakter:
    def __init__(self, ad, can, guc, ceviklik, dayaniklilik):
        self.ad = ad
        self.can = can
        self.guc = guc
        self.ceviklik = ceviklik
        self.dayaniklilik = dayaniklilik

# Oyuncu sınıfı
class Oyuncu(Karakter):
    def __init__(self, ad, enstruman):
        super().__init__(ad, 100, 1, 1, 1)  # Başlangıç değerleri
        self.enstruman = enstruman
        self.para = 10
        self.seviye = 1
        self.tecrube = 0
        self.tokluk = 100
        self.hijyen = 100
        self.eglence = 100
        self.uykusuzluk = 100
        self.karizma = 1
        self.toplayicilik = 1
        self.envanter = {"Şifalı Bitki": 0, "Av Eti": 0,"Büyük Balık": 0, "Orta Balık": 0, "Küçük Balık": 0,"Mantar": 0, "Odun": 0, "Taş": 0, "Metal": 0}
        self.ekili_tohumlar = []  # Added attribute
        self.urunler = []  # Added attribute to store harvested crops

    def __str__(self):
        return (f"Ad: {self.ad}\nEnstrüman: {self.enstruman}\nPara: {self.para}\nSeviye: {self.seviye}\n"
                f"Tecrübe: {self.tecrube}\nCan: {self.can}\nTokluk: {self.tokluk}\nHijyen: {self.hijyen}\n"
                f"Eğlence: {self.eglence}\nUykusuzluk: {self.uykusuzluk}\nGüç: {self.guc}\nÇeviklik: {self.ceviklik}\n"
                f"Dayanıklılık: {self.dayaniklilik}\nKarizma: {self.karizma}\nToplayıcılık: {self.toplayicilik}")

    def update_stats(self, action):
        if action != "sleep":
            self.tokluk = max(self.tokluk - 10, 0)
            self.hijyen = max(self.hijyen - 10, 0)
            self.eglence = max(self.eglence - 10, 0)
        else:
            self.tokluk = max(self.tokluk - 30, 0)
            self.hijyen = max(self.hijyen - 30, 0)
            self.eglence = max(self.eglence - 30, 0)

        self.check_warnings()
        self.check_status()

    def check_warnings(self):
        if self.tokluk <= 20:
            print("Uyarı: Acıktınız.")
        if self.hijyen <= 20:
            print("Uyarı: Hijyeniniz azaldı.")
        if self.eglence <= 20:
            print("Uyarı: Eğlenceniz azaldı.")
        if self.uykusuzluk <= 20:
            print("Uyarı: Uykunuz geldi.")

    def check_status(self):
        if self.can <= 0 or self.tokluk <= 0:
            print("Karakteriniz öldü! Oyun bitti.")
            pygame.quit()
            sys.exit()
        if self.hijyen <= 0:
            print("Hijyeniniz çok düşük, handa şarkı söyleyemezsiniz.")
        if self.eglence <= 0:
            print("Eğlenceniz çok düşük, maceraya atılamazsınız.")

# Metin çizdirme fonksiyonu
def draw_text_with_background(text, font, text_color, bg_color, surface, x, y, padding_x=20, padding_y=10):
    textobj = font.render(text, True, text_color)
    textrect = textobj.get_rect(center=(x, y))
    bgrect = pygame.Rect(textrect.left - padding_x, textrect.top - padding_y, textrect.width + 2 * padding_x, textrect.height + 2 * padding_y)
    pygame.draw.rect(surface, bg_color, bgrect, border_radius=20)
    surface.blit(textobj, textrect)

# Can barı çizdirme fonksiyonu
def draw_health_bar(surface, x, y, health, max_health, bar_color):
    bar_length = 200
    bar_height = 20
    fill = (health / max_health) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, bar_color, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# Müzik dosyalarını yükleyin
music_files = {
    'intro': 'intro.mp3',
    'battle': 'battle.mp3',
    'classical': 'classical.mp3'
}

# Müzik çalma fonksiyonu
def soundtrack(track):
    pygame.mixer.music.load(music_files[track])
    pygame.mixer.music.play(-1)  # Sonsuz döngüde çal


# Font ayarları (fantasy_font.ttf dosyasını kullanın)
fantasy_font = pygame.font.Font('fantasy_font.ttf', 22)
small_fantasy_font = pygame.font.Font('fantasy_font.ttf', 13)

# Metin animasyon fonksiyonu
def draw_text_with_animation(lines, font, color, surface, x, y, delay=50):
    y_offset = 0
    for line in lines:
        text_surface = font.render('', True, color)
        text_rect = text_surface.get_rect(center=(x, y + y_offset))
        for i in range(len(line)):
            surface.blit(background_images['intro'], (0, 0))  # Arka planı yeniden çiz
            for prev_line in lines[:lines.index(line)]:
                prev_surface = font.render(prev_line, True, color)
                prev_rect = prev_surface.get_rect(center=(x, y + y_offset - (len(lines) - lines.index(prev_line)) * 30))
                surface.blit(prev_surface, prev_rect)
            text_surface = font.render(line[:i+1], True, color)
            surface.blit(text_surface, text_rect)
            pygame.display.flip()
            pygame.time.delay(delay)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    return
        y_offset += 30

# Açılış ekranı fonksiyonu
def intro_screen():
    soundtrack('intro')  # Klasik müziği çal
    intro_running = True
    screen.blit(background_images['intro'], (0, 0))
    
    # Metinleri daha küçük parçalara böldük ve ortaladık
    lines = [
        "Bir zamanlar,"
        "büyülü ormanların derinliklerinde...",
        "Kahraman bir müzisyen,",
        "destansı maceralara atılmak için",
        "yola çıktı.",
        "Bu müzisyen, gizemli diyarların",
        "sırlarını keşfetmek ve..",
        "efsanevi hazineleri bulmak için...",
        "Büyük tehlikelerle yüzleşmeye hazırdı.",
        "Başlamak için herhangi bir tuşa basın."
    ]
    
    draw_text_with_animation(lines[:-1], fantasy_font, WHITE, screen, screen_width / 2, screen_height / 2 - 150)
    draw_text_with_animation([lines[-1]], fantasy_font, WHITE, screen, screen_width / 2, screen_height - 100)
    
    while intro_running:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intro_running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                intro_running = False

# Ana menü fonksiyonu
def main_menu(oyuncu):
    soundtrack('classical')  # Klasik müziği çal
    menu_items = [
        ("Kamp alanına git", camp_site),
        ("Şifahaneye git", healing_house),
        ("Hana git", tavern),
        ("Çiftliğe git", farm),
        ("Maceraya atıl", adventure),
        ("Seviye atla", level_up),
        ("Durumu göster", show_status),
        ("Envanteri görüntüle", envanteri_goster),
        ("Oyundan çık", exit_game)  # exit_game fonksiyonunu burada çağırın
    ]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['menu'], (0, 0))
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, (label, _) in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    action = menu_items[selected_item][1]
                    action(oyuncu)
                    if selected_item == len(menu_items) - 1:
                        running = False


def envanteri_goster(oyuncu):
    running = True
    while running:
        screen.blit(background_images['showstatus'], (0, 0))
        draw_text_with_background('Envanter', font, BLACK, WHITE, screen, screen_width / 2, 20)

        attributes = [
            f"Şifalı Bitki: {oyuncu.envanter.get('Şifalı Bitki', 0)}",
            f"Av Eti: {oyuncu.envanter.get('Av Eti', 0)}",
            f"Mantar: {oyuncu.envanter.get('Mantar', 0)}",
            f"Büyük Balık: {oyuncu.envanter.get('Büyük Balık', 0)}",
            f"Orta Balık: {oyuncu.envanter.get('Orta Balık', 0)}",
            f"Küçük Balık: {oyuncu.envanter.get('Küçük Balık', 0)}",
            f"Tohum: {oyuncu.envanter.get('Tohum',0)}",
            f"Odun: {oyuncu.envanter.get('Odun', 0)}",
            f"Taş: {oyuncu.envanter.get('Taş', 0)}",
            f"Metal: {oyuncu.envanter.get('Metal', 0)}"
        ]

        for idx, attr in enumerate(attributes):
            draw_text_with_background(attr, font, BLACK, WHITE, screen, screen_width / 2, 60 + idx * 30)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu(oyuncu)


# Kamp alanı fonksiyonu
def camp_site(oyuncu):
    menu_items = ["Kamp ateşinin başında çalgı çal/şarkı söyle",
                  "Nehirde yıkan",
                  "Çadırına girip uyu",
                  "Nehirde balık tut",
                  "Köy meydanına dön"]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['campsite'], (0, 0))
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, label in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected_item == 0:
                        oyuncu.eglence = min(oyuncu.eglence + 20, 100)
                        oyuncu.tecrube += 10
                        oyuncu.update_stats('normal')
                        print("Çalgı çaldınız ve şarkı söylediniz. Eğlence ve tecrübe puanınız arttı.")
                    elif selected_item == 1:
                        oyuncu.hijyen = 100
                        oyuncu.update_stats('normal')
                        print("Nehirde yıkandınız. Hijyeniniz maksimuma ulaştı.")
                    elif selected_item == 2:
                        oyuncu.uykusuzluk = 100
                        oyuncu.update_stats('sleep')
                        print("Uyudunuz. Uykusuzluk seviyeniz maksimuma ulaştı.")
                    elif selected_item == 3:
                        balık_tut(oyuncu)
                        oyuncu.update_stats('normal')
                    elif selected_item == 4:
                        running = False
                        main_menu(oyuncu)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu(oyuncu)

def balık_tut(oyuncu):
    balık_olasılık = random.randint(1, 100)
    if balık_olasılık <= 10:
        oyuncu.envanter["Büyük Balık"] = oyuncu.envanter.get("Büyük Balık", 0) + 1
        print("Büyük balık tuttunuz!")
    elif balık_olasılık <= 30:
        oyuncu.envanter["Orta Balık"] = oyuncu.envanter.get("Orta Balık", 0) + 1
        print("Orta balık tuttunuz!")
    elif balık_olasılık <= 60:
        oyuncu.envanter["Küçük Balık"] = oyuncu.envanter.get("Küçük Balık", 0) + 1
        print("Küçük balık tuttunuz!")
    else:
        print("Balık tutamadınız.")

# Şifahane fonksiyonu
def healing_house(oyuncu):
    menu_items = ["Şifacıdan yaralarını sarmasını iste",
                  "Şifacıdan merhem yapıp sürmesini iste",
                  "Envanteri sat ve para kazan",
                  "Köy meydanına dön"]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['healinghouse'], (0, 0))
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, label in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected_item == 0:
                        oyuncu.can = min(oyuncu.can + 20, 100)
                        oyuncu.update_stats('normal')
                        print("Şifacı yaralarınızı sardı. Canınız arttı.")
                    elif selected_item == 1:
                        oyuncu.can = min(oyuncu.can + 50, 100)
                        oyuncu.update_stats('normal')
                        print("Şifacı merhem yaptı ve sürdü. Canınız önemli ölçüde arttı.")
                    elif selected_item == 2:
                        sell_inventory(oyuncu)
                        oyuncu.update_stats('normal')
                    elif selected_item == 3:
                        running = False
                        main_menu(oyuncu)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu(oyuncu)

# Envanteri satma fonksiyonu
def sell_inventory(oyuncu):
    prices = {"Şifalı Bitki": 15, "Av Eti": 25, "Mantar": 50, "Büyük Balık": 40, "Orta Balık": 27, "Küçük Balık": 13}
    total_value = 0
    for item, amount in oyuncu.envanter.items():
        total_value += amount * prices.get(item, 0)
        oyuncu.envanter[item] = 0

    oyuncu.para += total_value
    print(f"Envanterinizdeki ürünleri {total_value} TL karşılığında sattınız.")

# Han fonksiyonu
def tavern(oyuncu):
    menu_items = [
        ("Yiyecek satın al ve ye", buy_food),
        ("İçecek satın al, iç ve eğlen", buy_drink),
        ("Balık sat", sell_fish),
        ("Enstrüman çal ve şarkı söyle", lambda oyuncu: [play_music(oyuncu), main_menu(oyuncu)]),
        ("Loto oyna", lambda oyuncu: [loto_oyna(oyuncu), main_menu(oyuncu)]),
        ("Köy meydanına dön", main_menu)
    ]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['tavern'], (0, 0))
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, (label, _) in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)

        draw_text_with_background(f"Cüzdan: {oyuncu.para} TL", small_font, WHITE, LIGHT_RED, screen, screen_width / 2, screen_height - 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    action = menu_items[selected_item][1]
                    action(oyuncu)
                    if selected_item == len(menu_items) - 1:
                        running = False

def sell_fish(oyuncu):
    prices = {"Büyük Balık": 40, "Orta Balık": 27, "Küçük Balık": 14}
    total_value = 0
    for fish in ["Büyük Balık", "Orta Balık", "Küçük Balık"]:
        if oyuncu.envanter.get(fish, 0) > 0:
            total_value += oyuncu.envanter[fish] * prices[fish]
            oyuncu.envanter[fish] = 0

    oyuncu.para += total_value
    print(f"Balıklarınızı {total_value} TL karşılığında sattınız.")

# Yiyecek satın alma fonksiyonu
def buy_food(oyuncu):
    food_items = {"Pizza": 15, "Ekmek": 5, "Elma": 3, "Tavuk": 20, "Kebap": 25, "Çorba": 10}
    basket = {}
    total_cost = 0
    running = True

    while running:
        screen.blit(background_images['food'], (0, 0))

        draw_text_with_background('Yiyecekler:', small_font, BLACK, WHITE, screen, screen_width / 2, 20)
        y_offset = 50
        for idx, (item, price) in enumerate(food_items.items()):
            draw_text_with_background(f"{item} - {price} TL", small_font, BLACK, WHITE, screen, screen_width / 2, y_offset + idx * 30)
            if basket.get(item, 0) > 0:
                draw_text_with_background(f"Seçilen: {basket[item]}", small_font, BLACK, WHITE, screen, screen_width / 2 + 200, y_offset + idx * 30)

        draw_text_with_background(f"Toplam: {total_cost} TL", small_font, BLACK, WHITE, screen, screen_width / 2, screen_height - 60)
        draw_text_with_background('Sepeti Onayla', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 60)
        draw_text_with_background('Sepeti Temizle', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 30)
        draw_text_with_background('Önceki Menüye Dön', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 90)
        draw_text_with_background(f"Cüzdan: {oyuncu.para} TL", small_font, BLACK, WHITE, screen, screen_width / 2, screen_height - 30)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for idx, (item, price) in enumerate(food_items.items()):
                    if screen_width / 2 - 100 <= mouse_x <= screen_width / 2 + 100 and y_offset + idx * 30 <= mouse_y <= y_offset + idx * 30 + 20:
                        basket[item] = basket.get(item, 0) + 1
                        total_cost += price

                if screen_width - 200 <= mouse_x <= screen_width - 20:
                    if screen_height - 60 <= mouse_y <= screen_height - 40:
                        if total_cost <= oyuncu.para:
                            oyuncu.para -= total_cost
                            for item, quantity in basket.items():
                                if item == "Pizza":
                                    oyuncu.tokluk = min(oyuncu.tokluk + 40 * quantity, 100)
                                elif item == "Ekmek":
                                    oyuncu.tokluk = min(oyuncu.tokluk + 10 * quantity, 100)
                                elif item == "Elma":
                                    oyuncu.tokluk = min(oyuncu.tokluk + 5 * quantity, 100)
                                elif item == "Tavuk":
                                    oyuncu.tokluk = min(oyuncu.tokluk + 50 * quantity, 100)
                                elif item == "Kebap":
                                    oyuncu.tokluk = min(oyuncu.tokluk + 60 * quantity, 100)
                                elif item == "Çorba":
                                    oyuncu.tokluk = min(oyuncu.tokluk + 20 * quantity, 100)
                            oyuncu.update_stats("normal")
                            print(f"Yiyecekleri {total_cost} TL karşılığında satın aldınız. Tokluk: {oyuncu.tokluk}")
                            running = False
                            main_menu(oyuncu)
                        else:
                            print("Yeterli paranız yok.")
                    elif screen_height - 30 <= mouse_y <= screen_height - 10:
                        basket.clear()
                        total_cost = 0
                        print("Sepet temizlendi.")
                    elif screen_height - 90 <= mouse_y <= screen_height - 70:
                        running = False
                        main_menu(oyuncu)

# İçecek satın alma fonksiyonu
def buy_drink(oyuncu):
    drink_items = {"Su": 2, "Meyve Suyu": 7, "Bira": 12, "Kola": 5, "Ayran": 3, "Çay": 4}
    basket = {}
    total_cost = 0
    running = True
    while running:
        screen.blit(background_images['drink'], (0, 0))

        draw_text_with_background('İçecekler:', small_font, BLACK, WHITE, screen, screen_width / 2, 20)
        y_offset = 50
        for idx, (item, price) in enumerate(drink_items.items()):
            draw_text_with_background(f"{item} - {price} TL", small_font, BLACK, WHITE, screen, screen_width / 2, y_offset + idx * 30)
            if basket.get(item, 0) > 0:
                draw_text_with_background(f"Seçilen: {basket[item]}", small_font, BLACK, WHITE, screen, screen_width / 2 + 200, y_offset + idx * 30)

        draw_text_with_background(f"Toplam: {total_cost} TL", small_font, BLACK, WHITE, screen, screen_width / 2, screen_height - 60)
        draw_text_with_background('Sepeti Onayla', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 60)
        draw_text_with_background('Sepeti Temizle', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 30)
        draw_text_with_background('Önceki Menüye Dön', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 90)
        draw_text_with_background(f"Cüzdan: {oyuncu.para} TL", small_font, BLACK, WHITE, screen, screen_width / 2, screen_height - 30)


        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for idx, (item, price) in enumerate(drink_items.items()):
                    if screen_width / 2 - 100 <= mouse_x <= screen_width / 2 + 100 and y_offset + idx * 30 <= mouse_y <= y_offset + idx * 30 + 20:
                        basket[item] = basket.get(item, 0) + 1
                        total_cost += price

                if screen_width - 200 <= mouse_x <= screen_width - 20:
                    if screen_height - 60 <= mouse_y <= screen_height - 40:
                        if total_cost <= oyuncu.para:
                            oyuncu.para -= total_cost
                            oyuncu.eglence = min(oyuncu.eglence + 30, 100)
                            oyuncu.update_stats("normal")
                            print(f"İçecekleri {total_cost} TL karşılığında satın aldınız.")
                            running = False
                            main_menu(oyuncu)
                        else:
                            print("Yeterli paranız yok.")
                    elif screen_height - 30 <= mouse_y <= screen_height - 10:
                        basket.clear()
                        total_cost = 0
                        print("Sepet temizlendi.")
                    elif screen_height - 90 <= mouse_y <= screen_height - 70:
                        running = False
                        main_menu(oyuncu)

# Enstrüman çalma fonksiyonu
def play_music(oyuncu):
    if oyuncu.hijyen > 0:
        oyuncu.eglence = min(oyuncu.eglence + 10, 100)
        oyuncu.tecrube += 20
        oyuncu.para += 10 + oyuncu.karizma
        oyuncu.update_stats("normal")
        print("Enstrüman çaldınız ve şarkı söylediniz. Eğlence ve tecrübe puanınız, ayrıca para kazandınız.")
    else:
        print("Hijyen düşük, performans sergileyemezsiniz.")

# Loto oynama
def loto_oyna(oyuncu):
    if oyuncu.para >= 10:
        oyuncu.para -= 10
        kazanma_sansi = random.randint(1, 100)
        if kazanma_sansi <= 20:
            kazanilan_para = random.randint(20, 100)
            oyuncu.para += kazanilan_para
            oyuncu.update_stats("normal")
            print(f"Tebrikler! Lotodan {kazanilan_para} TL kazandınız. Mevcut paranız: {oyuncu.para} TL")
        else:
            print("Maalesef, lotodan kazanamadınız.")
    else:
        print("Yeterli paranız yok.")

def farm(oyuncu):
    menu_items = [
        ("Tohum satın al ve ekmek için hazırla", buy_seed),
        ("Tarlaya git ve tohum ekmek", plant_seeds),
        ("Ürünleri topla", harvest_crops),
        ("Ustaya git", ustaya_git),
        ("Çiftliği terk et", main_menu)
    ]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['farm'], (0, 0))
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, (label, _) in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)

        draw_text_with_background(f"Cüzdan: {oyuncu.para} TL", small_font, WHITE, LIGHT_RED, screen, screen_width / 2, screen_height - 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    action = menu_items[selected_item][1]
                    action(oyuncu)
                    if selected_item == len(menu_items) - 1:
                        running = False
def buy_seed(oyuncu):
    seed_items = {"Buğday Tohumu": 5, "Mısır Tohumu": 7, "Domates Tohumu": 10}
    basket = {}
    total_cost = 0
    running = True
    while running:
        screen.blit(background_images['farm'], (0, 0))

        draw_text_with_background('Tohumlar:', small_font, BLACK, WHITE, screen, screen_width / 2, 20)
        y_offset = 50
        for idx, (item, price) in enumerate(seed_items.items()):
            draw_text_with_background(f"{item} - {price} TL", small_font, BLACK, WHITE, screen, screen_width / 2, y_offset + idx * 30)
            if basket.get(item, 0) > 0:
                draw_text_with_background(f"Seçilen: {basket[item]}", small_font, BLACK, WHITE, screen, screen_width / 2 + 200, y_offset + idx * 30)

        draw_text_with_background(f"Toplam: {total_cost} TL", small_font, BLACK, WHITE, screen, screen_width / 2, screen_height - 60)
        draw_text_with_background('Sepeti Onayla', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 60)
        draw_text_with_background('Sepeti Temizle', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 30)
        draw_text_with_background('Önceki Menüye Dön', small_font, BLACK, WHITE, screen, screen_width - 200, screen_height - 90)
        draw_text_with_background(f"Cüzdan: {oyuncu.para} TL", small_font, BLACK, WHITE, screen, screen_width / 2, screen_height - 30)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for idx, (item, price) in enumerate(seed_items.items()):
                    if screen_width / 2 - 100 <= mouse_x <= screen_width / 2 + 100 and y_offset + idx * 30 <= mouse_y <= y_offset + idx * 30 + 20:
                        basket[item] = basket.get(item, 0) + 1
                        total_cost += price

                if screen_width - 200 <= mouse_x <= screen_width - 20:
                    if screen_height - 60 <= mouse_y <= screen_height - 40:
                        if total_cost <= oyuncu.para:
                            oyuncu.para -= total_cost
                            for item, quantity in basket.items():
                                oyuncu.envanter[item] = oyuncu.envanter.get(item, 0) + quantity
                            print(f"Tohumları {total_cost} TL karşılığında satın aldınız.")
                            running = False
                        else:
                            print("Yeterli paranız yok.")
                    elif screen_height - 30 <= mouse_y <= screen_height - 10:
                        basket.clear()
                        total_cost = 0
                        print("Sepet temizlendi.")
                    elif screen_height - 90 <= mouse_y <= screen_height - 70:
                        running = False

# Tohum Ekleme Fonksiyonu
def plant_seeds(oyuncu):
    seeds = {key: value for key, value in oyuncu.envanter.items() if "Tohum" in key}
    if not seeds:
        print("Tohumunuz yok.")
        return

    selected_seed = None
    while selected_seed not in seeds:
        print("Ekilecek tohumu seçin:")
        for idx, seed in enumerate(seeds):
            print(f"{idx + 1}. {seed}")
        choice = input("Seçiminiz: ")
        if choice.isdigit() and 1 <= int(choice) <= len(seeds):
            selected_seed = list(seeds.keys())[int(choice) - 1]

    if selected_seed:
        oyuncu.envanter[selected_seed] -= 1
        if oyuncu.envanter[selected_seed] == 0:
            del oyuncu.envanter[selected_seed]
        oyuncu.ekili_tohumlar.append((selected_seed, 0))
        print(f"{selected_seed} ekildi.")

# Ürün Hasadı Fonksiyonu
def harvest_crops(oyuncu):
    ready_crops = [seed for seed, days in oyuncu.ekili_tohumlar if 2 <= days <= 5]
    for crop in ready_crops:
        oyuncu.urunler.append(crop[0].replace("Tohum", ""))
        oyuncu.ekili_tohumlar.remove(crop)
    if ready_crops:
        print("Ürünleriniz olgunlaştı ve envanterinize eklendi.")
    else:
        print("Henüz hasat edilecek ürün yok.")

def ustaya_git(oyuncu):
    menu_items = [
        ("Odun sat", lambda oyuncu: malzeme_sat(oyuncu, "Odun")),
        ("Taş sat", lambda oyuncu: malzeme_sat(oyuncu, "Taş")),
        ("Metal sat", lambda oyuncu: malzeme_sat(oyuncu, "Metal")),
        ("Bıçak satın al (2x güç)", lambda oyuncu: esya_satın_al(oyuncu, "Bıçak", 2, 50)),
        ("Balta satın al (3x güç)", lambda oyuncu: esya_satın_al(oyuncu, "Balta", 3, 100)),
        ("Kılıç satın al (4x güç)", lambda oyuncu: esya_satın_al(oyuncu, "Kılıç", 4, 150)),
        ("Tahta zırh al (2x dayanıklılık)", lambda oyuncu: esya_satın_al(oyuncu, "Tahta Zırh", 2, 50, zırh=True)),
        ("Taş zırh al (3x dayanıklılık)", lambda oyuncu: esya_satın_al(oyuncu, "Taş Zırh", 3, 100, zırh=True)),
        ("Metal zırh al (4x dayanıklılık)", lambda oyuncu: esya_satın_al(oyuncu, "Metal Zırh", 4, 150, zırh=True)),
        ("Geri dön", main_menu)
    ]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['usta'], (0, 0))
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, (label, _) in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)
        
        # Cüzdan bilgisini sol üst köşeye gelsin
        draw_text_with_background(f"Cüzdan: {oyuncu.para} TL", small_font, WHITE, LIGHT_RED, screen, 100, 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    action = menu_items[selected_item][1]
                    action(oyuncu)
                    if selected_item == len(menu_items) - 1:
                        running = False

def malzeme_sat(oyuncu, malzeme):
    fiyatlar = {"Odun": 10, "Taş": 15, "Metal": 20}
    if oyuncu.envanter[malzeme] > 0:
        oyuncu.para += fiyatlar[malzeme] * oyuncu.envanter[malzeme]
        oyuncu.envanter[malzeme] = 0
        print(f"Tüm {malzeme} malzemelerini sattınız.")
    else:
        print(f"Satılacak {malzeme} yok.")
    main_menu(oyuncu)

def esya_satın_al(oyuncu, esya, guc_bonus, fiyat, zırh=False):
    if oyuncu.para >= fiyat:
        oyuncu.para -= fiyat
        if zırh:
            oyuncu.dayaniklilik += guc_bonus
        else:
            oyuncu.guc += guc_bonus
        print(f"{esya} satın aldınız. {'Dayanıklılığınız' if zırh else 'Gücünüz'} arttı.")
    else:
        print("Yeterli paranız yok.")
    main_menu(oyuncu)

def adventure(oyuncu):
    menu_items = [
        "Yakın çevreden şifalı bitki topla ve avlan",
        "Ormanı keşfe çık (kolay)",
        "Kayalıkları keşfe çık (orta)",
        "Vadiyi keşfe çık (zor)",
        "Malzeme Bul",
        "Köy meydanına dön"
    ]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['forest'], (0, 0))
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, label in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    handle_adventure_selection(oyuncu, selected_item)
                    if selected_item == 4:
                        running = False
                        main_menu(oyuncu)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu(oyuncu)

def handle_adventure_selection(oyuncu, selected_item):
    if selected_item == 0:
        toplayicilik_kullan(oyuncu)
        oyuncu.update_stats('normal')
        main_menu(oyuncu)
    elif selected_item == 1:
        dusman = Karakter("Güçsüz Haydut", 50, random.randint(1, 5), random.randint(1, 5), random.randint(1, 5))
        savas(oyuncu, dusman)
    elif selected_item == 2:
        dusman = Karakter("Orta Seviye Haydut", 70, random.randint(6, 10), random.randint(6, 10), random.randint(6, 10))
        savas(oyuncu, dusman)
    elif selected_item == 3:
        dusman = Karakter("Güçlü Haydut", 90, random.randint(11, 15), random.randint(11, 15), random.randint(11, 15))
        savas(oyuncu, dusman)
    elif selected_item == 4:
        malzeme_bulma_menusu(oyuncu)

def toplayicilik_kullan(oyuncu):
    bitki_sansi = random.randint(1, 100)
    if bitki_sansi <= oyuncu.toplayicilik * 4:
        oyuncu.envanter["Şifalı Bitki"] += 1
        print("Şifalı bitki buldunuz ve envanterinize eklendi.")
    else:
        print("Şifalı bitki bulamadınız.")

    av_sansi = random.randint(1, 100)
    if av_sansi <= oyuncu.toplayicilik * 2:
        oyuncu.envanter["Av Eti"] += 1
        print("Başarılı bir av yaptınız ve av eti envanterinize eklendi.")
    else:
        print("Av yapamadınız.")

    mantar_sansi = random.randint(1, 100)
    if mantar_sansi <= 10:
        oyuncu.envanter["Mantar"] = oyuncu.envanter.get("Mantar", 0) + 1
        print("Mantar buldunuz!")

def malzeme_bulma_menusu(oyuncu):
    menu_items = [
        "Odun kes",
        "Taş topla",
        "Metal ara",
        "Geri dön"
    ]
    selected_item = 0
    running = True
    while running:
        screen.blit(background_images['collect'], (0, 0))  # Malzeme bulma arka planı
        total_items = len(menu_items)
        start_y = screen_height / 2 - (total_items * 20)

        for idx, label in enumerate(menu_items):
            if idx == selected_item:
                bg_color = DARK_RED
                text_color = HOVER_COLOR
            else:
                bg_color = LIGHT_RED
                text_color = FONT_COLOR
            draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected_item == 0:
                        odun_kes(oyuncu)
                    elif selected_item == 1:
                        tas_topla(oyuncu)
                    elif selected_item == 2:
                        metal_ara(oyuncu)
                    elif selected_item == 3:
                        running = False
                        main_menu(oyuncu)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu(oyuncu)

def odun_kes(oyuncu):
    odun_miktari = random.randint(1, 5)
    oyuncu.envanter["Odun"] += odun_miktari
    print(f"{odun_miktari} odun kestiniz ve envanterinize eklendi.")
    oyuncu.update_stats('normal')
    malzeme_bulma_menusu(oyuncu)

def tas_topla(oyuncu):
    tas_miktari = random.randint(1, 5)
    oyuncu.envanter["Taş"] += tas_miktari
    print(f"{tas_miktari} taş topladınız ve envanterinize eklendi.")
    oyuncu.update_stats('normal')
    malzeme_bulma_menusu(oyuncu)

def metal_ara(oyuncu):
    metal_miktari = random.randint(1, 3)
    oyuncu.envanter["Metal"] += metal_miktari
    print(f"{metal_miktari} metal buldunuz ve envanterinize eklendi.")
    oyuncu.update_stats('normal')
    malzeme_bulma_menusu(oyuncu)

def savas(oyuncu, dusman):
    soundtrack('battle')  # Klasik müziği çal
    running = True
    esya_kullanildi = False
    while running:
        screen.blit(background_images['fight'], (0, 0))

        draw_text_with_background(f"{oyuncu.ad}", font, BLACK, WHITE, screen, screen_width / 2, 20)
        draw_health_bar(screen, 20, 60, oyuncu.can, 100, GREEN)

        draw_text_with_background(f"{dusman.ad}", font, BLACK, WHITE, screen, screen_width / 2, 100)
        draw_health_bar(screen, screen_width - 220, 60, dusman.can, 100, RED)

        draw_text_with_background("Saldır (S) / Kaç (K)", font, BLACK, WHITE, screen, screen_width / 2, 140)
        draw_text_with_background("Ana menüye dönmek için ESC'ye basınız", font, BLACK, WHITE, screen, screen_width / 2, 180)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if not esya_kullanildi:
                        if "Bıçak" in oyuncu.envanter:
                            oyuncu.guc *= 2
                            esya_kullanildi = True
                        elif "Balta" in oyuncu.envanter:
                            oyuncu.guc *= 3
                            esya_kullanildi = True
                        elif "Kılıç" in oyuncu.envanter:
                            oyuncu.guc *= 4
                            esya_kullanildi = True
                    zarar = oyuncu_hamle(oyuncu, dusman)
                    if dusman.can <= 0:
                        print(f"{dusman.ad} yenildi!")
                        oyuncu_tecrube_ve_para_kazan(oyuncu, dusman)
                        running = False
                        main_menu(oyuncu)
                    else:
                        dusman_hamle(dusman, oyuncu)
                        if oyuncu.can <= 0:
                            print("Öldünüz! Oyun bitti.")
                            pygame.quit()
                            sys.exit()
                    if esya_kullanildi:
                        oyuncu.guc //= 2 if "Bıçak" in oyuncu.envanter else 3 if "Balta" in oyuncu.envanter else 4
                elif event.key == pygame.K_k:
                    if kacis_basarili(oyuncu.ceviklik):
                        print("Başarıyla kaçtınız!")
                        running = False
                        main_menu(oyuncu)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu(oyuncu)

def oyuncu_hamle(oyuncu, dusman):
    zarar = saldiri_hesapla(oyuncu.guc)
    dusman.can = max(dusman.can - savunma_hesapla(zarar, dusman.dayaniklilik), 0)
    print(f"{oyuncu.ad} {zarar} hasar verdi. Düşmanın kalan canı: {dusman.can}")
    return zarar

def dusman_hamle(dusman, oyuncu):
    zarar = saldiri_hesapla(dusman.guc)
    oyuncu.can = max(oyuncu.can - savunma_hesapla(zarar, oyuncu.dayaniklilik), 0)
    print(f"{dusman.ad} {zarar} hasar verdi. Kalan canınız: {oyuncu.can}")
    return zarar

def saldiri_hesapla(guc):
    return 4 * guc

def savunma_hesapla(verilen_hasar, dayaniklilik):
    azaltma = verilen_hasar * (4 * dayaniklilik / 100)
    alinan_hasar = verilen_hasar - azaltma
    return max(alinan_hasar, 1)

def kacis_basarili(ceviklik):
    zar = random.randint(2 * ceviklik, 100)
    return zar > 50

def oyuncu_tecrube_ve_para_kazan(oyuncu, dusman):
    tecrube_kazanci = 30 if dusman.ad == "Güçsüz Haydut" else 60 if dusman.ad == "Orta Seviye Haydut" else 100
    para_kazanci = tecrube_kazanci
    oyuncu.tecrube += tecrube_kazanci
    oyuncu.para += para_kazanci
    print(f"Tecrübe puanınız: {oyuncu.tecrube}, Paranız: {oyuncu.para}")

def level_up(oyuncu):
    if oyuncu.tecrube >= 100:
        menu_items = [
            "Güç artır (2x saldırı gücü)",
            "Çeviklik artır (hasardan daha az etkilenme)",
            "Dayanıklılık artır (hasardan daha az etkilenme)",
            "Karizma artır (daha fazla para kazanma)",
            "Toplayıcılık artır (şifalı bitki bulma ihtimali artar)",
            "Ana menüye dön"
        ]
        selected_item = 0
        running = True

        while running:
            screen.blit(background_images['levelup'], (0, 0))
            draw_text_with_background('Seviye Atlama Menüsü', font, BLACK, WHITE, screen, screen_width / 2, 20)

            total_items = len(menu_items)
            start_y = screen_height / 2 - (total_items * 20)

            for idx, label in enumerate(menu_items):
                if idx == selected_item:
                    bg_color = DARK_RED
                    text_color = HOVER_COLOR
                else:
                    bg_color = LIGHT_RED
                    text_color = FONT_COLOR
                draw_text_with_background(label, font, text_color, bg_color, screen, screen_width / 2, start_y + idx * 50)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_item = (selected_item - 1) % len(menu_items)
                    elif event.key == pygame.K_DOWN:
                        selected_item = (selected_item + 1) % len(menu_items)
                    elif event.key == pygame.K_RETURN:
                        if selected_item == 0:
                            oyuncu.guc += 1
                            print("Güç artırıldı. Saldırı gücünüz iki katına çıktı.")
                        elif selected_item == 1:
                            oyuncu.ceviklik += 1
                            print("Çeviklik artırıldı. Hasardan daha az etkilenirsiniz.")
                        elif selected_item == 2:
                            oyuncu.dayaniklilik += 1
                            print("Dayanıklılık artırıldı. Hasardan daha az etkilenirsiniz.")
                        elif selected_item == 3:
                            oyuncu.karizma += 1
                            print("Karizma artırıldı. Enstrüman çalarken daha fazla para kazanırsınız.")
                        elif selected_item == 4:
                            oyuncu.toplayicilik += 1
                            print("Toplayıcılık artırıldı. Şifalı bitki bulma ihtimaliniz arttı.")
                        oyuncu.tecrube -= 100
                        oyuncu.seviye += 1
                        running = False
                        main_menu(oyuncu)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        main_menu(oyuncu)
    else:
        print("Yeterli tecrübe puanınız yok.")

def show_status(oyuncu):
    running = True
    while running:
        screen.blit(background_images['showstatus'], (0, 0))
        draw_text_with_background('Oyuncu Durumu', fantasy_font, BLACK, WHITE, screen, screen_width / 2, 20)

        # Sağ ve sol sütunlar için metinleri böldük
        left_attributes = [
            f"Ad: {oyuncu.ad}",
            f"Can: {oyuncu.can}",
            f"Tokluk: {oyuncu.tokluk}",
            f"Hijyen: {oyuncu.hijyen}",
            f"Eğlence: {oyuncu.eglence}"
        ]
        
        right_attributes = [
            f"Seviye: {oyuncu.seviye}",
            f"Tecrübe: {oyuncu.tecrube}",
            f"Güç: {oyuncu.guc}",
            f"Çeviklik: {oyuncu.ceviklik}",
            f"Dayanıklılık: {oyuncu.dayaniklilik}",
            f"Karizma: {oyuncu.karizma}",
            f"Toplayıcılık: {oyuncu.toplayicilik}",
            f"Para: {oyuncu.para}"
        ]

        # Sol sütundaki metinleri çiz
        for idx, attr in enumerate(left_attributes):
            draw_text_with_background(attr, fantasy_font, BLACK, WHITE, screen, screen_width / 4, 60 + idx * 60)

        # Sağ sütundaki metinleri çiz
        for idx, attr in enumerate(right_attributes):
            draw_text_with_background(attr, fantasy_font, BLACK, WHITE, screen, 3 * screen_width / 4, 60 + idx * 60)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu(oyuncu)

def exit_game(oyuncu):
    global running
    running = False
    pygame.quit()
    sys.exit()

def game_loop():
    global running
    running = True
    ad = input("Oyuncunun adını girin: ")
    enstruman = input("Oyuncunun enstrümanını girin: ")
    oyuncu = Oyuncu(ad, enstruman)  # Burada oyuncu nesnesini oluşturun
    intro_screen()  # Giriş ekranını gösterin
    while running:
        main_menu(oyuncu)  # oyuncu nesnesini parametre olarak geçirin
    pygame.quit()
    sys.exit()

# Oyunu başlat
game_loop()


