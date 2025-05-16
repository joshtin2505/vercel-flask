# API de Métodos Numéricos para Integración

Esta API permite calcular integrales definidas de funciones matemáticas utilizando diferentes métodos numéricos. Soporta funciones en formato Python y LaTeX.

## Requisitos
- Python 3.10+
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

### Respuesta con Tablas de Iteración
Todos los métodos incluyen ahora una tabla de iteración en la respuesta. Esta tabla muestra el paso a paso del cálculo realizado con los siguientes campos para cada punto evaluado:

- **i**: Índice o posición del punto
- **xi**: Valor de x en ese punto
- **f(xi)**: Valor de la función evaluada en ese punto
- **coeficiente**: Factor multiplicador según el método
- **f(xi) * coef**: Resultado del producto

Esto te permite seguir en detalle cómo se realizó el cálculo y verificar los resultados paso a paso.

### Parámetro 'n' en los métodos numéricos
El parámetro `n` representa el número de subintervalos o divisiones utilizadas en los cálculos. Un valor mayor de `n` generalmente proporciona una aproximación más precisa de la integral, pero requiere más cálculos.

Cada método tiene diferentes valores predeterminados y restricciones para `n`:
- **Método del Trapecio**: n=10 por defecto, sin restricciones específicas
- **Método de Jorge Boole**: n=4 por defecto, debe ser múltiplo de 4 (se ajusta automáticamente)
- **Método de Simpson 3/8**: n=3 por defecto, debe ser múltiplo de 3 (se ajusta automáticamente)
- **Método de Simpson 1/3**: debe ser par (se ajusta automáticamente)
- **Método de Simpson Abierto**: valor predeterminado de n=4


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
- **Parámetros:**
  - `funcion`: Expresión matemática a integrar
  - `formato`: Formato de la función (python o latex)
  - `a`: Límite inferior de integración
  - `b`: Límite superior de integración
  - `n`: Número de subintervalos (valor predeterminado: 10)
- **Respuesta:** Resultado de la integral, parámetros usados y una tabla de iteración que muestra cada punto evaluado con su valor de x, f(x), coeficiente aplicado (1 para extremos, 2 para puntos intermedios) y producto.

### 4. Método de Jorge Boole
- **POST /boole**
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
- **Parámetros:**
  - `funcion`: Expresión matemática a integrar
  - `formato`: Formato de la función (python o latex)
  - `a`: Límite inferior de integración
  - `b`: Límite superior de integración
  - `n`: Número de subintervalos (valor predeterminado: 4, debe ser múltiplo de 4)
  
  **Nota:** Si `n` no es múltiplo de 4, el método ajustará automáticamente este valor.
- **Respuesta:** Resultado de la integral, parámetros usados y una tabla de iteración que muestra los puntos evaluados organizados por segmentos, con información sobre sus coeficientes (7, 32, 12, 32, 7) y valores calculados.

### 5. Método de Simpson 3/8
- **POST /simpson38**
- **Body (JSON):**
  ```json
  {
    "funcion": "x^2 + 2*x + 1",
    "formato": "python" | "latex",
    "a": 0,
    "b": 1,
    "n": 3
  }
  ```
- **Parámetros:**
  - `funcion`: Expresión matemática a integrar
  - `formato`: Formato de la función (python o latex)
  - `a`: Límite inferior de integración
  - `b`: Límite superior de integración
  - `n`: Número de subintervalos (valor predeterminado: 3, debe ser múltiplo de 3)
  
  **Nota:** Si `n` no es múltiplo de 3, el método ajustará automáticamente este valor.
- **Respuesta:** Resultado de la integral, parámetros usados y una tabla de iteración que muestra cada punto evaluado con su valor de x, f(x), y los coeficientes aplicados (1 para extremos, 3 para puntos con índice 1,2,4,5,7,8,..., y 2 para puntos con índice 3,6,9,...).

### 6. Método de Simpson 1/3
- **POST /simpson13**
- **Body (JSON):**
  ```json
  {
    "funcion": "x^2 + 2*x + 1",
    "formato": "python" | "latex",
    "a": 0,
    "b": 1,
    "n": 2
  }
  ```
- **Parámetros:**
  - `funcion`: Expresión matemática a integrar
  - `formato`: Formato de la función (python o latex)
  - `a`: Límite inferior de integración
  - `b`: Límite superior de integración
  - `n`: Número de subintervalos (debe ser par)
  
  **Nota:** Si `n` no es par, el método ajustará automáticamente este valor.
- **Respuesta:** Resultado de la integral, parámetros usados y una tabla de iteración que muestra cada punto evaluado con su valor de x, f(x), y los coeficientes aplicados (1 para extremos, 4 para puntos con índice impar, y 2 para puntos con índice par).

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
- **Parámetros:**
  - `funcion`: Expresión matemática a integrar
  - `formato`: Formato de la función (python o latex)
  - `a`: Límite inferior de integración
  - `b`: Límite superior de integración
  - `n`: Número de subintervalos (valor predeterminado: 4)
- **Respuesta:** Resultado de la integral, parámetros usados y una tabla de iteración que muestra los puntos evaluados internos (los extremos a y b no se evalúan en este método) con sus respectivos coeficientes (2 para puntos con índice impar, 1 para puntos con índice par).

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
