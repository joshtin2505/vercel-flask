# API de Métodos Numéricos para Integración

Esta API permite calcular integrales definidas de funciones matemáticas utilizando diferentes métodos numéricos. Soporta funciones en formato Python y LaTeX.

## Requisitos
- Python 3.8+
- pip

## Instalación y ejecución local

1. **Clona el repositorio y entra a la carpeta raíz:**
   ```bash
   git clone <URL-del-repo>
   cd vercel-flask
   ```
2. **Crea y activa un entorno virtual:**
   ```bash
   python -m venv .venv
   ```
   ```bash
   # En Windows:
   .venv\Scripts\activate
   ```
   ```bash
   # En Mac/Linux:
   source .venv/bin/activate
   ```
3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Establece la variable de entorno para la carpeta raíz del proyecto:**
   ```bash
   # En PowerShell:
   $env:FLASK_APP = "api/index.py"
   ```
5. **Ejecuta el servidor Flask:**
   ```bash
   flask run
   ```

La API estará disponible en: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## Documentación de Endpoints

### 1. Home
- **GET /**
- **Descripción:** Mensaje de bienvenida de la API.
- **Respuesta:**
  ```text
  API de Métodos Numéricos para Integración
  ```

### 2. Obtener información de métodos
- **GET /metodos**
- **Descripción:** Devuelve la lista de métodos numéricos disponibles, formatos soportados y ejemplo de petición.
- **Respuesta:** JSON con los métodos y ejemplos.

### 3. Método del Trapecio
- **POST /trapecio**
- **Body (JSON):**
  ```json
  {
    "funcion": "x^2 + 2*x + 1",
    "formato": "python" | "latex",
    "a": 0,
    "b": 1,
    "n": 10
  }
  ```
- **Respuesta:** Resultado de la integral y parámetros usados.

### 4. Método de Jorge Boole
- **POST /boole**
- **Body (JSON):** Igual que el anterior, pero `n` debe ser múltiplo de 4.
- **Respuesta:** Resultado de la integral y parámetros usados.

### 5. Método de Simpson 3/8
- **POST /simpson38**
- **Body (JSON):** Igual que el anterior, pero `n` debe ser múltiplo de 3.
- **Respuesta:** Resultado de la integral y parámetros usados.

### 6. Método de Simpson 1/3
- **POST /simpson13**
- **Body (JSON):** Igual que el anterior, pero `n` debe ser par.
- **Respuesta:** Resultado de la integral y parámetros usados.

### 7. Método de Simpson Abierto
- **POST /simpson_abierto**
- **Body (JSON):**
  ```json
  {
    "funcion": "x^2 + 2*x + 1",
    "formato": "python" | "latex",
    "a": 0,
    "b": 1,
    "n": 4
  }
  ```
- **Respuesta:** Resultado de la integral y parámetros usados.

---

## Formatos soportados
- **python:** Sintaxis estándar de Python (`x**2 + 2*x + 1`)
- **latex:** Sintaxis LaTeX (`x^2 + 2x + 1`, `\exp{-x^{2}}`)

---

## Ejemplo de petición (LaTeX)
```json
{
  "funcion": "\\exp{-x^{2}}",
  "formato": "latex",
  "a": 0,
  "b": 2,
  "n": 10
}
```

---

## Notas
- Si usas formato LaTeX y tu función incluye `\exp{-x^{2}}`, puedes usar también `e^{-x^{2}}`.
- Todos los endpoints devuelven errores claros si la función no es válida o los parámetros son incorrectos.
