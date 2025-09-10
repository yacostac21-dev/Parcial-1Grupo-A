import re

class AnalizadorLexico:
    """FASE 1: Análisis Léxico - Convierte código en tokens"""
    
    def __init__(self):
        self.reservadas = {'INSERT', 'SHOW', 'estudiante', 'curso'}
        self.patron_nombre = re.compile(r'^[a-zA-Z]+$')
        self.patron_codigo_est = re.compile(r'^202[0-9]-[0-9]{5}$')
        self.patron_codigo_cur = re.compile(r'^[A-Z]{3}[0-9]{3}$')
    
    def tokenizar(self, linea):
        """Convierte una línea en tokens clasificados"""
        elementos = linea.strip().split()
        tokens = []
        
        for elemento in elementos:
            # Separar punto y coma
            if elemento.endswith(';'):
                if len(elemento) > 1:
                    tokens.append(self._clasificar(elemento[:-1]))
                tokens.append(';')
            else:
                tokens.append(self._clasificar(elemento))
        
        return tokens
    
    def _clasificar(self, token):
        """Clasifica un token según su tipo"""
        if token in self.reservadas:
            return ('RESERVADA', token)
        elif self.patron_codigo_est.match(token):
            return ('CODIGO_EST', token)
        elif self.patron_codigo_cur.match(token):
            return ('CODIGO_CUR', token)
        elif self.patron_nombre.match(token):
            return ('NOMBRE', token)
        else:
            return ('ERROR', token)

class AnalizadorSintactico:
    """FASE 2: Análisis Sintáctico - Verifica gramática"""
    
    def __init__(self):
        self.pos = 0
        self.tokens = []
    
    def analizar(self, tokens):
        """Verifica que los tokens sigan la gramática"""
        self.tokens = tokens
        self.pos = 0
        
        try:
            if not tokens:
                return False, "Instrucción vacía"
            
            # Verificar estructura según gramática
            if self._actual() == ('RESERVADA', 'INSERT'):
                return self._parsear_insert()
            elif self._actual() == ('RESERVADA', 'SHOW'):
                return self._parsear_show()
            else:
                return False, "Debe comenzar con INSERT o SHOW"
                
        except IndexError:
            return False, "Instrucción incompleta"
    
    def _actual(self):
        """Token actual"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def _avanzar(self):
        """Avanza al siguiente token"""
        self.pos += 1
    
    def _parsear_insert(self):
        """INSERT estudiante <nombre> <codigo_est> | INSERT curso <nombre> <codigo_cur>"""
        self._avanzar()  # Consumir INSERT
        
        if self._actual() == ('RESERVADA', 'estudiante'):
            self._avanzar()
            # Esperar: nombre codigo_estudiante ;
            if self._actual()[0] != 'NOMBRE':
                return False, "Se esperaba nombre del estudiante"
            nombre = self._actual()[1]
            self._avanzar()
            
            if self._actual()[0] != 'CODIGO_EST':
                return False, "Se esperaba código del estudiante"
            codigo = self._actual()[1]
            self._avanzar()
            
        elif self._actual() == ('RESERVADA', 'curso'):
            self._avanzar()
            # Esperar: nombre codigo_curso ;
            if self._actual()[0] != 'NOMBRE':
                return False, "Se esperaba nombre del curso"
            nombre = self._actual()[1]
            self._avanzar()
            
            if self._actual()[0] != 'CODIGO_CUR':
                return False, "Se esperaba código del curso"
            codigo = self._actual()[1]
            self._avanzar()
        else:
            return False, "Después de INSERT debe ir 'estudiante' o 'curso'"
        
        # Verificar punto y coma final
        if self._actual() != ';':
            return False, "Falta ';' al final"
        
        return True, ""
    
    def _parsear_show(self):
        """SHOW estudiante <nombre> | SHOW curso <codigo_cur>"""
        self._avanzar()  # Consumir SHOW
        
        if self._actual() == ('RESERVADA', 'estudiante'):
            self._avanzar()
            if self._actual()[0] != 'NOMBRE':
                return False, "Se esperaba nombre del estudiante"
            self._avanzar()
            
        elif self._actual() == ('RESERVADA', 'curso'):
            self._avanzar()
            if self._actual()[0] != 'CODIGO_CUR':
                return False, "Se esperaba código del curso"
            self._avanzar()
        else:
            return False, "Después de SHOW debe ir 'estudiante' o 'curso'"
        
        # Verificar punto y coma final
        if self._actual() != ';':
            return False, "Falta ';' al final"
        
        return True, ""

class AnalizadorSemantico:
    """FASE 3: Análisis Semántico - Valida formatos con regex"""
    
    def __init__(self):
        self.regex_codigo_est = re.compile(r'^202[0-9]-[0-9]{5}$')
        self.regex_codigo_cur = re.compile(r'^[A-Z]{3}[0-9]{3}$')
    
    def validar(self, tokens):
        """Valida semánticamente los códigos"""
        for token in tokens:
            if isinstance(token, tuple):
                tipo, valor = token
                if tipo == 'CODIGO_EST':
                    if not self.regex_codigo_est.match(valor):
                        return False, f"código de estudiante inválido ({valor})"
                elif tipo == 'CODIGO_CUR':
                    if not self.regex_codigo_cur.match(valor):
                        return False, f"código de curso inválido ({valor})"
                elif tipo == 'ERROR':
                    return False, f"token inválido ({valor})"
            else:
                # Es el punto y coma o algo más
                continue
        
        return True, ""

class CompiladorMiniSQL:
    """Compilador completo que integra las 3 fases"""
    
    def __init__(self):
        self.lexico = AnalizadorLexico()
        self.sintactico = AnalizadorSintactico()
        self.semantico = AnalizadorSemantico()
    
    def compilar(self, linea):
        """Compila una instrucción completa"""
        # Ignorar líneas vacías y comentarios
        if not linea.strip() or linea.strip().startswith('#'):
            return ""
        
        # FASE 1: Análisis Léxico
        tokens = self.lexico.tokenizar(linea)
        
        # FASE 2: Análisis Sintáctico
        sintaxis_ok, error_sintactico = self.sintactico.analizar(tokens)
        if not sintaxis_ok:
            return f"Error: {error_sintactico}"
        
        # FASE 3: Análisis Semántico
        semantica_ok, error_semantico = self.semantico.validar(tokens)
        if not semantica_ok:
            return f"Error: {error_semantico}"
        
        # Si todo está bien
        return "Instrucción válida: ejecutada"
    
    def procesar_archivo(self, contenido):
        """Procesa múltiples instrucciones"""
        lineas = contenido.strip().split('\n')
        resultados = []
        
        for linea in lineas:
            resultado = self.compilar(linea)
            if resultado:  # Solo agregar si no está vacío
                resultados.append(resultado)
        
        return resultados

# Programa principal
def main():
    compilador = CompiladorMiniSQL()
    
    # Leer archivo programa.txt si existe
    try:
        with open('programa.txt', 'r') as archivo:
            contenido = archivo.read()
            print("=== PROCESANDO ARCHIVO programa.txt ===")
            resultados = compilador.procesar_archivo(contenido)
            
            for resultado in resultados:
                print(resultado)
    except FileNotFoundError:
        print("Archivo programa.txt no encontrado. Usando ejemplo por defecto:")
        
        # Ejemplo del enunciado
        programa = """INSERT estudiante Juan 2025-12345;
INSERT curso Compiladores SIS305;
SHOW estudiante Juan;
SHOW curso MAT101;
INSERT curso BasesDeDatos MATH01;"""
        
        print("=== COMPILADOR MiniSQL-U ===")
        resultados = compilador.procesar_archivo(programa)
        
        for resultado in resultados:
            print(resultado)
    
    # Opción para probar instrucciones individuales
    print("\n" + "="*50)
    print("MODO INTERACTIVO - Ingresa instrucciones (o 'salir' para terminar):")
    
    while True:
        try:
            instruccion = input("\n> ")
            if instruccion.lower() == 'salir':
                break
            
            resultado = compilador.compilar(instruccion)
            if resultado:
                print(resultado)
                
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break

if __name__ == "__main__":
    main()