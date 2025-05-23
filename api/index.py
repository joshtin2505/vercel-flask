from flask import Flask, request, jsonify
import numpy as np
import sympy as sp
import re
from sympy.parsing.latex import parse_latex
from sympy import symbols
from sympy.utilities.lambdify import lambdify
# Configuración para permitir consultas de cualquier origen (CORS)

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
@app.route('/')
def home():
    return 'API de Métodos Numéricos para Integración'

# Función para evaluar expresiones LaTeX de forma general
# Esta función no depende de casos específicos, sino que utiliza
# el poder del módulo sympy para convertir cualquier expresión LaTeX válida

# Función para evaluar expresiones matemáticas de forma segura
def evaluar_funcion(funcion, x, formato="python"):
    try:
        if formato == "latex":
            # Preprocesar para soportar tanto 'e^{...}' como '\exp{...}'
            def reemplazar_e_exponencial(expr):
                # Reemplaza e^{...} por \exp{...} usando regex
                pattern = r"e\s*\^\s*\{([^}]*)\}"
                return re.sub(pattern, r"\\exp{\1}", expr)
            funcion_preprocesada = reemplazar_e_exponencial(funcion)
            try:
                # Paso 1: Convertir la expresión LaTeX a expresión simbólica
                expr_sympy = parse_latex(funcion_preprocesada)
                # Paso 2: Crear una función numérica a partir de la expresión simbólica
                f_numeric = lambdify('x', expr_sympy, 'numpy')
                # Paso 3: Evaluar la función numérica con el valor de x
                try:
                    resultado = f_numeric(x)
                    if isinstance(resultado, complex):
                        if abs(resultado.imag) < 1e-10:
                            return float(resultado.real)
                        else:
                            return float(abs(resultado))
                    return float(resultado)
                except Exception as e_eval:
                    x_symbol = sp.Symbol('x')
                    resultado = expr_sympy.subs(x_symbol, x).evalf()
                    return float(resultado)
            except Exception as e_parse:
                # Si todo lo anterior falla, intentamos una evaluación alternativa
                try:
                    x_sym = symbols('x')
                    expr = parse_latex(funcion_preprocesada)
                    resultado = expr.subs(x_sym, x).evalf()
                    return float(resultado)
                except Exception as e_final:
                    raise ValueError(f"No se pudo evaluar la expresión LaTeX. Error: {str(e_final)}")
        else:
            # Evaluación estándar para formato python
            return eval(funcion)
    except Exception as e:
        raise ValueError(f"Error al evaluar la función: {str(e)}")


# 1. Método del Trapecio    
@app.route('/trapecio', methods=['POST'])
def metodo_trapecio():
    try:
        data = request.get_json()
        funcion = data.get('funcion')
        formato = data.get('formato', 'python')  # Por defecto 'python', también acepta 'latex'
        a = float(data.get('a'))  # Límite inferior
        b = float(data.get('b'))  # Límite superior
        n = int(data.get('n', 10))  # Número de subintervalos
        
        if not funcion:
            return jsonify({"error": "Falta la función"}), 400
        
        h = (b - a) / n
        
        # Crear tabla de iteración
        tabla_iteracion = []
        
        # Agregar los extremos (a y b) a la tabla
        fa = evaluar_funcion(funcion, a, formato)
        fb = evaluar_funcion(funcion, b, formato)
        
        tabla_iteracion.append({
            "i": 0,
            "xi": a,
            "f(xi)": fa,
            "coeficiente": 1,
            "f(xi) * coef": fa
        })
        
        suma = fa
        # Calcular f(xi) para cada punto intermedio
        for i in range(1, n):
            x = a + i * h
            valor = evaluar_funcion(funcion, x, formato)
            coef = 2  # En el método del trapecio, todos los puntos intermedios tienen coeficiente 2
            suma += coef * valor
            
            tabla_iteracion.append({
                "i": i,
                "xi": x,
                "f(xi)": valor,
                "coeficiente": coef,
                "f(xi) * coef": coef * valor
            })
        
        # Agregar el punto final a la tabla
        tabla_iteracion.append({
            "i": n,
            "xi": b,
            "f(xi)": fb,
            "coeficiente": 1,
            "f(xi) * coef": fb
        })
        
        suma += fb
        integral = (h/2) * suma
        
        return jsonify({
            "resultado": integral,
            "metodo": "Trapecio",
            "funcion": funcion,
            "formato": formato,
            "a": a,
            "b": b,
            "n": n,
            "h": h,
            "tabla_iteracion": tabla_iteracion,
            "formula": "(h/2) * [f(a) + 2*f(x1) + 2*f(x2) + ... + 2*f(xn-1) + f(b)]"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 2. Método de Jorge Boole
@app.route('/boole', methods=['POST'])
def metodo_boole():
    try:
        data = request.get_json()
        funcion = data.get('funcion')
        formato = data.get('formato', 'python')  # Por defecto 'python', también acepta 'latex'
        a = float(data.get('a'))  # Límite inferior
        b = float(data.get('b'))  # Límite superior
        n = int(data.get('n', 4))  # Número de subintervalos (múltiplo de 4)
        
        if not funcion:
            return jsonify({"error": "Falta la función"}), 400
        
        # Asegurar que n es múltiplo de 4
        if n % 4 != 0:
            n = (n // 4) * 4
            if n == 0:
                n = 4
        
        h = (b - a) / n
        suma = 0
        
        # Crear tabla de iteración
        tabla_iteracion = []
        
        # Aplicar fórmula de Boole: (2h/45)[7f(x₀) + 32f(x₁) + 12f(x₂) + 32f(x₃) + 7f(x₄)]
        # Para múltiples segmentos
        segmentos_tabla = []
        
        for j in range(0, n, 4):
            x0 = a + j * h
            x1 = a + (j + 1) * h
            x2 = a + (j + 2) * h
            x3 = a + (j + 3) * h
            x4 = a + (j + 4) * h
            
            f0 = evaluar_funcion(funcion, x0, formato)
            f1 = evaluar_funcion(funcion, x1, formato)
            f2 = evaluar_funcion(funcion, x2, formato)
            f3 = evaluar_funcion(funcion, x3, formato)
            f4 = evaluar_funcion(funcion, x4, formato)
            
            # Agregar puntos a la tabla de iteración
            tabla_iteracion.append({
                "segmento": j // 4 + 1,
                "punto": "x0",
                "x": x0,
                "f(x)": f0,
                "coeficiente": 7,
                "f(x) * coef": 7 * f0
            })
            
            tabla_iteracion.append({
                "segmento": j // 4 + 1,
                "punto": "x1",
                "x": x1,
                "f(x)": f1,
                "coeficiente": 32,
                "f(x) * coef": 32 * f1
            })
            
            tabla_iteracion.append({
                "segmento": j // 4 + 1,
                "punto": "x2",
                "x": x2,
                "f(x)": f2,
                "coeficiente": 12,
                "f(x) * coef": 12 * f2
            })
            
            tabla_iteracion.append({
                "segmento": j // 4 + 1,
                "punto": "x3",
                "x": x3,
                "f(x)": f3,
                "coeficiente": 32,
                "f(x) * coef": 32 * f3
            })
            
            tabla_iteracion.append({
                "segmento": j // 4 + 1,
                "punto": "x4",
                "x": x4,
                "f(x)": f4,
                "coeficiente": 7,
                "f(x) * coef": 7 * f4
            })
            
            segmento = (2*h/45) * (7*f0 + 32*f1 + 12*f2 + 32*f3 + 7*f4)
            suma += segmento
            
            segmentos_tabla.append({
                "segmento": j // 4 + 1,
                "intervalo": [x0, x4],
                "valor": segmento
            })
        
        return jsonify({
            "resultado": suma,
            "metodo": "Jorge Boole",
            "funcion": funcion,
            "formato": formato,
            "a": a,
            "b": b,
            "n": n,
            "h": h,
            "tabla_iteracion": tabla_iteracion,
            "segmentos": segmentos_tabla,
            "formula": "(2h/45)[7f(x₀) + 32f(x₁) + 12f(x₂) + 32f(x₃) + 7f(x₄)]"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 3. Método de Simpson 3/8
@app.route('/simpson38', methods=['POST'])
def metodo_simpson38():
    try:
        data = request.get_json()
        funcion = data.get('funcion')
        formato = data.get('formato', 'python')  # Por defecto 'python', también acepta 'latex'
        a = float(data.get('a'))  # Límite inferior
        b = float(data.get('b'))  # Límite superior
        n = int(data.get('n', 3))  # Número de subintervalos (múltiplo de 3)
        
        if not funcion:
            return jsonify({"error": "Falta la función"}), 400
        
        # Asegurar que n es múltiplo de 3
        if n % 3 != 0:
            n = (n // 3) * 3
            if n == 0:
                n = 3
        
        h = (b - a) / n
        
        # Crear tabla de iteración
        tabla_iteracion = []
        
        # Evaluar el extremo a
        fa = evaluar_funcion(funcion, a, formato)
        tabla_iteracion.append({
            "i": 0,
            "xi": a,
            "f(xi)": fa,
            "coeficiente": 1,
            "f(xi) * coef": fa
        })
        
        suma = fa
        
        # Sumar términos con coeficientes 3 (puntos con índice 1, 4, 7, ...)
        for i in range(1, n, 3):
            x = a + i * h
            valor = evaluar_funcion(funcion, x, formato)
            coef = 3
            suma += coef * valor
            
            tabla_iteracion.append({
                "i": i,
                "xi": x,
                "f(xi)": valor,
                "coeficiente": coef,
                "f(xi) * coef": coef * valor
            })
        
        # Sumar términos con coeficientes 3 (puntos con índice 2, 5, 8, ...)
        for i in range(2, n, 3):
            x = a + i * h
            valor = evaluar_funcion(funcion, x, formato)
            coef = 3
            suma += coef * valor
            
            tabla_iteracion.append({
                "i": i,
                "xi": x,
                "f(xi)": valor,
                "coeficiente": coef,
                "f(xi) * coef": coef * valor
            })
        
        # Sumar términos con coeficientes 2 (puntos con índice 3, 6, 9, ...)
        for i in range(3, n, 3):
            x = a + i * h
            valor = evaluar_funcion(funcion, x, formato)
            coef = 2
            suma += coef * valor
            
            tabla_iteracion.append({
                "i": i,
                "xi": x,
                "f(xi)": valor,
                "coeficiente": coef,
                "f(xi) * coef": coef * valor
            })
        
        # Evaluar el extremo b
        fb = evaluar_funcion(funcion, b, formato)
        tabla_iteracion.append({
            "i": n,
            "xi": b,
            "f(xi)": fb,
            "coeficiente": 1,
            "f(xi) * coef": fb
        })
        
        suma += fb
        integral = (3*h/8) * suma
        
        # Ordenar tabla por el índice i
        tabla_iteracion.sort(key=lambda x: x["i"])
        
        return jsonify({
            "resultado": integral,
            "metodo": "Simpson 3/8",
            "funcion": funcion,
            "formato": formato,
            "a": a,
            "b": b,
            "n": n,
            "h": h,
            "tabla_iteracion": tabla_iteracion,
            "formula": "(3h/8) * [f(x0) + 3f(x1) + 3f(x2) + 2f(x3) + 3f(x4) + ... + f(xn)]"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 4. Método de Simpson 1/3
@app.route('/simpson13', methods=['POST'])
def metodo_simpson13():
    try:
        data = request.get_json()
        funcion = data.get('funcion')
        formato = data.get('formato', 'python')  # Por defecto 'python', también acepta 'latex'
        a = float(data.get('a'))  # Límite inferior
        b = float(data.get('b'))  # Límite superior
        n = int(data.get('n', 2))  # Número de subintervalos (par)
        
        if not funcion:
            return jsonify({"error": "Falta la función"}), 400
        
        # Asegurar que n es par
        if n % 2 != 0:
            n += 1
        
        h = (b - a) / n
        
        # Crear tabla de iteración
        tabla_iteracion = []
        
        # Evaluar el extremo a
        fa = evaluar_funcion(funcion, a, formato)
        tabla_iteracion.append({
            "i": 0,
            "xi": a,
            "f(xi)": fa,
            "coeficiente": 1,
            "f(xi) * coef": fa
        })
        
        suma = fa
        
        # Sumar términos con coeficientes 4 (impares)
        for i in range(1, n, 2):
            x = a + i * h
            valor = evaluar_funcion(funcion, x, formato)
            coef = 4
            suma += coef * valor
            
            tabla_iteracion.append({
                "i": i,
                "xi": x,
                "f(xi)": valor,
                "coeficiente": coef,
                "f(xi) * coef": coef * valor
            })
        
        # Sumar términos con coeficientes 2 (pares)
        for i in range(2, n, 2):
            x = a + i * h
            valor = evaluar_funcion(funcion, x, formato)
            coef = 2
            suma += coef * valor
            
            tabla_iteracion.append({
                "i": i,
                "xi": x,
                "f(xi)": valor,
                "coeficiente": coef,
                "f(xi) * coef": coef * valor
            })
        
        # Evaluar el extremo b
        fb = evaluar_funcion(funcion, b, formato)
        tabla_iteracion.append({
            "i": n,
            "xi": b,
            "f(xi)": fb,
            "coeficiente": 1,
            "f(xi) * coef": fb
        })
        
        suma += fb
        integral = (h/3) * suma
        
        # Ordenar tabla por el índice i
        tabla_iteracion.sort(key=lambda x: x["i"])
        
        return jsonify({
            "resultado": integral,
            "metodo": "Simpson 1/3",
            "funcion": funcion,
            "formato": formato,
            "a": a,
            "b": b,
            "n": n,
            "h": h,
            "tabla_iteracion": tabla_iteracion,
            "formula": "(h/3) * [f(x0) + 4f(x1) + 2f(x2) + 4f(x3) + ... + f(xn)]"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 5. Método de Simpson Abierto
@app.route('/simpson_abierto', methods=['POST'])
def metodo_simpson_abierto():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No se recibieron datos JSON válidos"}), 400

        funcion = data.get('funcion')
        if not funcion:
            return jsonify({"error": "Falta el parámetro 'funcion'"}), 400

        formato = data.get('formato', 'python')
        try:
            a = float(data.get('a'))
            b = float(data.get('b'))
        except (ValueError, TypeError):
            return jsonify({"error": "Los parámetros 'a' y 'b' deben ser números"}), 400

        # ---- CÁLCULO DE SIMPSON ABIERTO 1/3 ----
        h = (b - a) / 4.0

        # Puntos internos
        x1 = a + h
        x2 = a + 2*h
        x3 = a + 3*h

        # Evaluación de la función
        f1 = evaluar_funcion(funcion, x1, formato)
        f2 = evaluar_funcion(funcion, x2, formato)
        f3 = evaluar_funcion(funcion, x3, formato)

        # Fórmula de Simpson abierto
        integral = (4*h/3) * (2*f1 - f2 + 2*f3)

        # Tabla de iteración (opcional, muestra solo 3 puntos)
        tabla_iteracion = [
            {"i": 1, "xi": x1, "f(xi)": f1},
            {"i": 2, "xi": x2, "f(xi)": f2},
            {"i": 3, "xi": x3, "f(xi)": f3},
        ]

        return jsonify({
            "resultado": integral,
            "metodo": "Simpson Abierto 1/3",
            "funcion": funcion,
            "formato": formato,
            "a": a,
            "b": b,
            "h": h,
            "tabla_iteracion": tabla_iteracion,
            "formula": "(4h/3) [2f(x₁) - f(x₂) + 2f(x₃)]",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
# Endpoint para obtener información de los métodos disponibles
@app.route('/metodos', methods=['GET'])
def obtener_metodos():
    return jsonify({
        "metodos": [
            {
                "nombre": "Trapecio",
                "endpoint": "/trapecio",
                "descripcion": "Método del Trapecio para integración numérica",
                "formula": "I = (h/2)[f(x₀) + 2f(x₁) + 2f(x₂) + ... + 2f(xₙ₋₁) + f(xₙ)]",
                "formato_soportado": ["python", "latex"],
                "tabla_iteracion": "Incluye detalles de cada punto evaluado con índice, valor de x, f(x), coeficiente aplicado y producto"
            },
            {
                "nombre": "Jorge Boole",
                "endpoint": "/boole",
                "descripcion": "Método de Jorge Boole para integración numérica",
                "formula": "I = (2h/45)[7f(x₀) + 32f(x₁) + 12f(x₂) + 32f(x₃) + 7f(x₄)]",
                "formato_soportado": ["python", "latex"],
                "tabla_iteracion": "Incluye detalles de cada punto evaluado organizados por segmentos, con información sobre los coeficientes (7,32,12,32,7)"
            },
            {
                "nombre": "Simpson 3/8",
                "endpoint": "/simpson38",
                "descripcion": "Método de Simpson 3/8 para integración numérica",
                "formula": "I = (3h/8)[f(x₀) + 3f(x₁) + 3f(x₂) + 2f(x₃) + ... + f(xₙ)]",
                "formato_soportado": ["python", "latex"],
                "tabla_iteracion": "Incluye detalles de cada punto con sus respectivos coeficientes (1,3,3,2,...)"
            },
            {
                "nombre": "Simpson 1/3",
                "endpoint": "/simpson13",
                "descripcion": "Método de Simpson 1/3 para integración numérica",
                "formula": "I = (h/3)[f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + ... + f(xₙ)]",
                "formato_soportado": ["python", "latex"],
                "tabla_iteracion": "Incluye detalles de cada punto con sus respectivos coeficientes (1,4,2,4,...)"
            },
            {
                "nombre": "Simpson Abierto",
                "endpoint": "/simpson_abierto",
                "descripcion": "Método de Simpson Abierto para integración numérica",
                "formula": "I = 3h[f(x₁) + 2f(x₂) + f(x₃) + 2f(x₄) + ... ]",
                "formato_soportado": ["python", "latex"],
                "tabla_iteracion": "Incluye detalles de los puntos internos evaluados (los extremos no se evalúan en este método)"
            }
        ],
        "formatos": {
            "python": "Expresiones matemáticas en sintaxis de Python (ej: x**2 + 2*x + 1)",
            "latex": "Expresiones matemáticas en formato LaTeX (ej: x^2 + 2x + 1)"
        },
        "ejemplo_peticion": {
            "funcion": "x^2 + \\sin(x)",
            "formato": "latex",
            "a": 0,
            "b": 3.14,
            "n": 100
        },
        "respuesta_incluye": {
            "resultado": "Valor numérico de la integral",
            "metodo": "Nombre del método utilizado",
            "funcion": "Función evaluada",
            "formato": "Formato de la función (python o latex)",
            "a": "Límite inferior",
            "b": "Límite superior",
            "n": "Número de subintervalos",
            "h": "Tamaño del paso",
            "tabla_iteracion": "Tabla con los detalles de cada punto evaluado durante el cálculo",
            "formula": "Fórmula matemática aplicada"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)