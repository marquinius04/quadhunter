from flask import Flask, render_template_string, Response
import json
import quadhunter

app = Flask(__name__)

@app.route("/")
def website():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mis quads</title>
    </head>
    <body>
        <div id="resultados"></div>
        <script>
            const data_from_event = new EventSource('/stream_busqueda');
            data_from_event.onmessage = function(evento){
                const info = JSON.parse(evento.data);
                
                const contenedor = document.getElementById('resultados');
                const imagen = info.img_url ? info.img_url : "https://via.placeholder.com/400x800?text=Sin+Imagen";
                

                // Aquí añadimos también la variable del precio que extrajimos en Python
                contenedor.innerHTML += `
                    <div class="tarjeta">
                        <a href="${info.url}" target="_blank">
                            <img src="${info.img_url}" alt="Imagen del anuncio">
                            <div class="tarjeta-info">
                                <h3>${info.title}</h3>
                                <p class="precio">${info.price}</p>
                            </div>
                        </a>
                    </div>
                `;
            }

            // NUEVO: El cortafuegos definitivo
            data_from_event.onerror = function() {
                // En el momento en que Python termine de enviar anuncios y cierre la conexión,
                // o si hay algún corte, el navegador detectará un error.
                // Con esta instrucción le obligamos a colgar el teléfono y no llamar más.
                data_from_event.close(); 
            };
        </script>
    </body>
    """

    return render_template_string(html)


@app.route("/stream_busqueda")
def stream_busqueda():
    return Response(quadhunter.run_scraper(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(port=5000)