from playwright.sync_api import sync_playwright
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re

# 1. TRAINING DATA
QUAD_EXAMPLES = [
    # YAMAHA
    "yamaha raptor 700", "yamaha raptor 660", "yamaha raptor 350", "yamaha raptor 250", "yamaha raptor 125", "yamaha raptor 90", "yamaha raptor 50",
    "yamaha yfz 450", "yamaha yfz 450r", "yamaha yfz 50",
    "yamaha grizzly 700", "yamaha grizzly 550", "yamaha grizzly 450", "yamaha grizzly 350", "yamaha grizzly 125",
    "yamaha kodiak 700", "yamaha kodiak 450",
    "yamaha banshee 350", "yamaha blaster 200", "yamaha warrior 350", "yamaha timberwolf 250", "yamaha bruin 350", "yamaha wolverine 450",
    
    # SUZUKI
    "suzuki ltz 400", "suzuki ltz 250", "suzuki ltr 450", "suzuki ltr 50",
    "suzuki kingquad 750", "suzuki kingquad 500", "suzuki kingquad 400", "suzuki kingquad 300",
    "suzuki vinson 500", "suzuki eiger 400", "suzuki ozark 250", "suzuki quadrunner", "suzuki quadsport",
    
    # HONDA
    "honda trx 700xx", "honda trx 450", "honda trx 400", "honda trx 300", "honda trx 250", "honda trx 90",
    "honda rincon 680", "honda foreman 500", "honda foreman 450", "honda rubicon 520", "honda rubicon 500", "honda rancher 420", "honda rancher 350",
    
    # KAWASAKI
    "kawasaki kfx 700", "kawasaki kfx 450", "kawasaki kfx 400", "kawasaki kfx 90", "kawasaki kfx 50",
    "kawasaki brute force 750", "kawasaki brute force 650", "kawasaki brute force 300",
    "kawasaki prairie 700", "kawasaki prairie 400", "kawasaki prairie 360", "kawasaki bayou 300", "kawasaki bayou 250",
    
    # POLARIS
    "polaris sportsman 1000", "polaris sportsman 850", "polaris sportsman 570", "polaris sportsman 500", "polaris sportsman 450", "polaris sportsman 400", "polaris sportsman 90",
    "polaris scrambler 1000", "polaris scrambler 850", "polaris scrambler 500", "polaris scrambler 400",
    "polaris predator 500", "polaris outlaw 525", "polaris magnum 500", "polaris magnum 330", "polaris trail boss 330", "polaris trail blazer 250", "polaris phoenix 200",
    
    # CAN-AM
    "can am renegade 1000", "can am renegade 850", "can am renegade 570", "can am renegade 500",
    "can am outlander 1000", "can am outlander 850", "can am outlander 650", "can am outlander 570", "can am outlander 450",
    "can am ds 450", "can am ds 250", "can am ds 90", "can am ds 70",
    
    # OTHER BRANDS
    "kymco mxu 700", "kymco mxu 500", "kymco mxu 300", "kymco mxu 250", "kymco mxu 150", "kymco maxxer 450", "kymco maxxer 300", "kymco maxxer 250",
    "cfmoto cforce 1000", "cfmoto cforce 850", "cfmoto cforce 800", "cfmoto cforce 625", "cfmoto cforce 520", "cfmoto cforce 450", "cfmoto cforce 110",
    "arctic cat alterra 700", "arctic cat alterra 500", "arctic cat alterra 300", "arctic cat xc 450", "arctic cat mudpro",
    "tgb blade 1000", "tgb blade 600", "tgb blade 550", "tgb target 600",
    "linhai 500", "linhai 400", "linhai 300",
    "segway snarler at6", "segway snarler at5",
    "gas gas hp 450", "gas gas wild 450", "ktm xc 450", "ktm xc 525",
    
    # GENERIC
    "agricultural quad", "4x4 quad", "2x4 quad", "4x4 atv", "agricultural atv", "utility atv", "sport quad", "kids quad", "miniquad"
]

MOTO_EXAMPLES = [
    # YAMAHA
    "yamaha r1", "yamaha r6", "yamaha r3", "yamaha r125",
    "yamaha mt 10", "yamaha mt 09", "yamaha mt 07", "yamaha mt 03", "yamaha mt 125",
    "yamaha tracer 9", "yamaha tracer 7", "yamaha tenere 700",
    "yamaha tmax", "yamaha xmax", "yamaha nmax", "yamaha aerox", "yamaha jog",
    "yamaha wr 450", "yamaha wr 250", "yamaha fz6", "yamaha fazer", "yamaha dragstar",
    
    # HONDA
    "honda cbr 1000", "honda cbr 650r", "honda cbr 600", "honda cbr 500r",
    "honda cb 1000r", "honda cb 650r", "honda cb 500", "honda cb 125",
    "honda africa twin", "honda transalp", "honda nt1100", "honda goldwing", "honda hornet",
    "honda rebel 1100", "honda rebel 500",
    "honda forza", "honda pcx", "honda sh 125", "honda vision",
    "honda crf 450", "honda crf 250",
    
    # KAWASAKI
    "kawasaki ninja zx-10r", "kawasaki ninja zx-6r", "kawasaki ninja 650", "kawasaki ninja 400", "kawasaki ninja 125",
    "kawasaki z1000", "kawasaki z900", "kawasaki z800", "kawasaki z650", "kawasaki z400", "kawasaki z125",
    "kawasaki versys", "kawasaki vulcan", "kawasaki vulcan s",
    "kawasaki kx 450", "kawasaki kx 250",
    
    # SUZUKI
    "suzuki gsxr 1000", "suzuki gsxr 750", "suzuki gsxr 600",
    "suzuki gsx s1000", "suzuki gsx s750", "suzuki sv 650",
    "suzuki v strom 1050", "suzuki v strom 650",
    "suzuki burgman", "suzuki address",
    "suzuki hayabusa", "suzuki intruder", "suzuki rmz 450", "suzuki rmz 250",
    
    # KTM
    "ktm super duke", "ktm duke 1290", "ktm duke 890", "ktm duke 790", "ktm duke 390", "ktm duke 125",
    "ktm adventure 1290", "ktm adventure 890", "ktm adventure 390",
    "ktm rc 390", "ktm rc 125",
    "ktm exc 450", "ktm exc 300", "ktm exc 250", "ktm exc 125", "ktm sx 250",
    
    # BMW
    "bmw gs 1250", "bmw gs 1200", "bmw gs 850", "bmw gs 750", "bmw f800gs", "bmw gs 310",
    "bmw s1000rr", "bmw f900r", "bmw f900xr", "bmw r1250r",
    "bmw rt 1250", "bmw r18", "bmw c400x", "bmw ce 04",
    
    # DUCATI
    "ducati panigale v4", "ducati panigale v2", "ducati panigale",
    "ducati monster", "ducati streetfighter", "ducati diavel",
    "ducati multistrada", "ducati desertx", "ducati scrambler", "ducati supersport", "ducati hypermotard",
    
    # TRIUMPH
    "triumph speed triple", "triumph street triple", "triumph trident 660",
    "triumph tiger", "triumph scrambler 1200",
    "triumph bonneville", "triumph thruxton", "triumph bobber", "triumph rocket 3",
    
    # OTHER BRANDS
    "aprilia rsv4", "aprilia rs 660", "aprilia tuono", "aprilia sr", "aprilia rx",
    "harley davidson sportster", "harley davidson softail", "harley davidson touring", "harley davidson pan america", "harley davidson street glide", "harley davidson iron 883",
    "indian scout", "indian ftr", "indian chief",
    "royal enfield interceptor", "royal enfield himalayan", "royal enfield meteor", "royal enfield classic",
    "husqvarna norden 901", "husqvarna svartpilen", "husqvarna vitpilen", "husqvarna fe 350", "husqvarna te 300", "husqvarna fc 250",
    "gas gas ec 300", "gas gas ec 250", "gas gas mc 450",
    "beta rr 480", "beta rr 300", "beta rr 250",
    "sherco se 300", "rieju mrt", "derbi senda",
    
    # GENERIC
    "motocross bike", "enduro bike", "trail bike", "trial bike", "pit bike",
    "300 scooter", "125 scooter", "50 scooter", "maxiscooter", "moped", "motorcycle",
    "custom bike", "cafe racer", "naked bike", "touring bike"
]

vectorizer = TfidfVectorizer()
vectorizer.fit(QUAD_EXAMPLES + MOTO_EXAMPLES)

def check_quad_or_moto(title, page):
    """
    Calculates text similarity to distinguish between Quads and Motorbikes.

    :param title: The title of the advertisement
    :type title: str
    :param page: The Playwright page object used to fetch image attributes
    :type page: playwright.sync_api.Page
    :return: Image URL if it is a Quad, otherwise False
    :rtype: str | bool
    """
    text_vec = vectorizer.transform([title])
    quad_sim = cosine_similarity(text_vec, vectorizer.transform(QUAD_EXAMPLES)).max()
    moto_sim = cosine_similarity(text_vec, vectorizer.transform(MOTO_EXAMPLES)).max()

    # Threshold-based check to prioritize Quads over Motorbikes
    if quad_sim - moto_sim > 0.05:
        # Attempts to extract the source URL from the first tabpanel found
        try:
            return page.get_by_role("tabpanel").first.get_attribute("src")
        except:
            return "https://via.placeholder.com/800x600?text=No+Image"
    return False

def clean_resources(route):
    """
    Intercepts network requests to block unnecessary assets and speed up scraping.

    :param route: The Playwright route object to be evaluated
    :type route: playwright.sync_api.Route
    """
    if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
        route.abort()
    else:
        route.continue_()

def run_scraper():
    """
    Launches the web scraper to find new quads on Wallapop and yields results.

    :yield: Server-Sent Events formatted JSON string
    :rtype: generator
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context()
        
        # Main Search Page
        page = context.new_page()
        page.route("**/*", clean_resources)
        page.goto("https://es.wallapop.com/search?category_id=14000&keywords=quad&order_by=newest")

        try:
            page.get_by_role("button").get_by_text("Reject all").click()
        except:
            pass

        ads = page.locator(".item-card_ItemCard--vertical__CNrfk").all()

        # Detail Page Configuration
        detail_page = context.new_page()
        # Abort only non-essential styles/fonts to allow image loading logic
        detail_page.route("**/*", lambda route: route.abort() 
                          if route.request.resource_type in ["stylesheet", "font"] 
                          else route.continue_())
        
        visited_urls = set()

        for ad in ads:
            href = ad.get_attribute("href")
            title = ad.get_attribute("title")
            
            if not href or not title:
                continue

            # Filtering out toy/kids quads via regex
            if re.search(r"(infantil|niño|juguete)", title.lower()):
                continue

            url = "https://es.wallapop.com/" + href
            if url in visited_urls:
                continue
            visited_urls.add(url)

            price = ad.locator(".item-card_ItemCard__price__pVpdc").inner_text()

            # Verify category and extract image from detail page
            detail_page.goto(url)
            img_url = check_quad_or_moto(title, detail_page)

            if img_url:
                data = {
                    "title": title.title(),
                    "price": price,
                    "url": url,
                    "img_url": img_url
                }
                yield f"data: {json.dumps(data)}\n\n"

        detail_page.close()
        browser.close()

if __name__ == "__main__":
    """
    Main entry point for manual execution.
    """
    for result in run_scraper():
        print(result)