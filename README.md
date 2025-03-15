# Futelegram

## Futelo

- Un Futelo es un mensaje con maximo 6 de cada letra.
- Promueve creatividad a traves de la limitacion, ¿eh?
- La cantidad de digitos (0 a 9) no debe superar 6.
- Los      espacios      son     ilimitados,      aprovechalos      .
- ¡Hay un maximo de 6 simbolos! (que no es digito/letra/espacio)


## Futelini

- Futelini = Futelo pero gamer, con inventario, progresion y mas.
- Cada jugador tiene su inventario que limita sus mensajes 😳
- Se parte con cuatro letras: H, O, L, A.
- Consigues nuevas letras subiendo de nivel
- La primera vez consigues 25 letras, las siguientes 5
- ¡Subir de nivel es cada vez mas dificil!
- Primero subes mandando 1 mensaje, luego mandando 2, luego 3, y así...

## Development

Recomendable hacer un entorno virtual para instalar las dependencias.

### Instalando dependencias

```bash
pip install -r /path/to/requirements.txt
```

### Agregando dependencias

Instalar como siempre y luego:

```bash
pipreqs --force --encoding utf-8 --ignore .venv
```

## Telegram Bot

El bot tiene tres partes: el bot, la api y la mini app.

Para correr el bot solo es necesario dejar corriendo el archivo en python: `python futelo_boy.py`

Para correr la api, usamos fast api: `uvicorn api:app --reload`

Para la mini app, se debe hacer el bundle de frontend con:

```bash
cd webapp
npm run build
```

Esto creará una carpeta estática `webapp/dist` para hostearse.
