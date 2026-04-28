from flask import Flask, render_template_string, Response
import json
import quadhunter 

app = Flask(__name__)

@app.route("/")
def website():
    """
    Renders the main user interface containing the carousel and the display logic.

    :return: The HTML content of the web page processed by the template engine.
    :rtype: str
    """
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quadhunter</title>
        <style>
            @font-face {
                font-family: 'Braaap';
                src: url('/static/fonts/Braaap_S2.otf') format('opentype');
            }

            @font-face {
                font-family: 'Cross';
                src: url('/static/fonts/Cross_X.otf') format('opentype');
            }

            @font-face {
                font-family: 'Rickey';
                src: url('/static/fonts/Sloe_Gin_Rickey.otf') format('opentype');
            }

            /* --- RESET AND BASE STYLES --- */
            ol, li { list-style: none; margin: 0; padding: 0; }
            * { box-sizing: border-box; scrollbar-width: none; }
            *::-webkit-scrollbar { width: 0; }

            body { 
                max-width: 50rem; 
                margin: 0 auto; 
                padding: 4rem 1.25rem; 
                font-family: 'Lato'; 
                background: #12141d; 
                text-align: center; 
            }

            h1 { margin-bottom: 2rem; color: #ffffff; font-weight: 300; letter-spacing: 1px; font-family: 'Braaap'; font-size: 4rem}

            /* --- CAROUSEL CONTAINER --- */
            .carousel { 
                position: relative; 
                padding-top: 75%; 
                border-radius: 1.5rem; 
                border: 5px solid rgba(38, 42, 60, .75);
                overflow: hidden; 
                perspective: 100px; 
            }

            .carousel__viewport { 
                position: absolute; top: 0; right: 0; bottom: 0; left: 0; 
                display: flex; 
                overflow-x: scroll; 
                scroll-behavior: smooth; 
                scroll-snap-type: x mandatory; 
                z-index: 1;
            }
            
            .carousel__slide { 
                position: relative; 
                flex: 0 0 100%; 
                width: 100%; 
                background-color: #333; 
            }
            
            .slide-content { 
                width: 100%; 
                height: 100%; 
                display: flex; 
                text-decoration: none; 
                position: relative; 
            }

            .slide-content img { 
                width: 100%; 
                height: 100%; 
                object-fit: cover; 
                object-position: center; 
            }

            /* --- TEXT ANIMATION --- */
            .slide-info { 
                position: absolute; bottom: 0; left: 0; width: 100%; 
                background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); 
                padding: 3rem 1rem 3rem; 
                color: white; 
                text-align: center; 
                z-index: 2;
                opacity: 0; 
                transform: translateY(30px); 
                transition: opacity 0.8s ease-out, transform 0.8s ease-out;
            }

            .carousel__slide.is-visible .slide-info {
                opacity: 1;
                transform: translateY(0);
            }

            .slide-info h3 { margin: 0 0 0.25rem; font-size: 4rem; font-family: 'Rickey'; letter-spacing: 2.5px; }
            .slide-info p.price { margin: 0; font-size: 3rem; color: #3e9c35; font-weight: bold; font-family: 'Cross'; text-shadow: 2px 0 #000, -2px 0 #000, 0 2px #000, 0 -2px #000,
             1px 1px #000, -1px -1px #000, 1px -1px #000, -1px 1px #000;}

            /* --- FIXED NAVIGATION BUTTONS --- */
            .carousel__btn { 
                position: absolute; 
                top: 50%; 
                transform: translateY(-50%); 
                width: 3.5rem; 
                height: 3.5rem; 
                border-radius: 50%; 
                background-color: rgba(0,0,0,0.6); 
                color: white; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                border: 2px solid white; 
                text-decoration: none; 
                z-index: 100; 
                cursor: pointer; 
                font-size: 1.5rem;
                transition: background-color 0.3s, opacity 0.3s, transform 0.2s;
            }

            .carousel__btn:hover { background-color: rgba(0,0,0,0.8); transform: translateY(-50%) scale(1.1); }
            
            .carousel__btn.hidden { opacity: 0; pointer-events: none; }

            #btn-prev { left: 1rem; }
            #btn-next { right: 1rem; }

            /* --- NAVIGATION DOTS --- */
            .carousel__navigation { 
                position: absolute; 
                right: 0; 
                bottom: 0.8rem; 
                left: 0; 
                text-align: center; 
                z-index: 20; 
            }

            .carousel__navigation-list {
                display: flex; 
                justify-content: center; 
                align-items: center;
                gap: 0.5rem;
                padding: 0;
            }

            .carousel__navigation-button { 
                display: block; 
                width: 0.75rem; 
                height: 0.75rem; 
                background-color: rgba(255,255,255,0.5); 
                border-radius: 50%; 
                font-size: 0;
                transition: background-color 0.3s, transform 0.2s;
            }
            .carousel__navigation-button:hover { 
                background-color: white; 
                transform: scale(1.2); 
            }
        </style>
    </head>
    <body>
        <h1>Quadhunter</h1>
        
        <section class="carousel">
            <a href="#" id="btn-prev" class="carousel__btn hidden">⟨</a>
            <a href="#" id="btn-next" class="carousel__btn hidden">⟩</a>

            <ol class="carousel__viewport" id="carousel-viewport"></ol>

            <aside class="carousel__navigation">
                <ol class="carousel__navigation-list" id="carousel-nav"></ol>
            </aside>
        </section>

        <script>
            let slideCount = 0;
            let currentActiveIndex = 1;
            const viewport = document.getElementById('carousel-viewport');
            const navList = document.getElementById('carousel-nav');
            const btnPrev = document.getElementById('btn-prev');
            const btnNext = document.getElementById('btn-next');

            function updateButtonLinks() {
                if (slideCount <= 1) {
                    btnPrev.classList.add('hidden');
                    btnNext.classList.add('hidden');
                    return;
                }
                btnPrev.classList.remove('hidden');
                btnNext.classList.remove('hidden');

                const prevIndex = currentActiveIndex > 1 ? currentActiveIndex - 1 : slideCount;
                const nextIndex = currentActiveIndex < slideCount ? currentActiveIndex + 1 : 1;

                btnPrev.href = `#carousel__slide${prevIndex}`;
                btnNext.href = `#carousel__slide${nextIndex}`;
            }

            viewport.addEventListener('scroll', () => {
                const index = Math.round(viewport.scrollLeft / viewport.offsetWidth) + 1;
                if (index !== currentActiveIndex) {
                    currentActiveIndex = index;
                    updateButtonLinks();
                }
            });

            const observerOptions = { root: viewport, threshold: 0.6 };
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) entry.target.classList.add('is-visible');
                    else entry.target.classList.remove('is-visible');
                });
            }, observerOptions);

            const eventSource = new EventSource('/stream_search');

            eventSource.onmessage = function(event) {
                const info = JSON.parse(event.data);
                slideCount++;
                
                const slideId = `carousel__slide${slideCount}`;
                const li = document.createElement('li');
                li.id = slideId;
                li.className = 'carousel__slide';
                
                const imageUrl = info.img_url ? info.img_url : "https://via.placeholder.com/800x600?text=No+Image";

                li.innerHTML = `
                    <a href="${info.url}" target="_blank" class="slide-content">
                        <img src="${imageUrl}" alt="${info.title}">
                        <div class="slide-info">
                            <h3>${info.title}</h3>
                            <p class="price">${info.price}</p>
                        </div>
                    </a>
                `;
                
                viewport.appendChild(li);
                observer.observe(li);

                const navLi = document.createElement('li');
                navLi.className = 'carousel__navigation-item';
                navLi.innerHTML = `<a href="#${slideId}" class="carousel__navigation-button"></a>`;
                navList.appendChild(navLi);

                updateButtonLinks();
            };

            eventSource.onerror = () => eventSource.close();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/stream_search")
def stream_search():
    """
    Manages real-time data transmission via Server-Sent Events (SSE).

    :return: A response configured for continuous data streaming to the browser.
    :rtype: flask.Response
    """
    return Response(quadhunter.run_scraper(), mimetype='text/event-stream')

if __name__ == "__main__":
    """
    Application entry point that starts the local web server.
    """
    app.run(port=5000)