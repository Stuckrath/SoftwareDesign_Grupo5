# SoftwareDesign_Grupo5
Avances hechos para el trabajo semestral de Diseño de Software (501352), de parte del grupo 5
### Nombre de archivos:
-Diagrama de comunicación (Creación): diagrama_comunicacion_objetos.png
-Diagrama de comunicación (Consulta): 
-Diagrama de clases refinado:DiagramaClase_v2.png
-Patrones de diseños aplicados (creacional): Patron_Builder.png
-Patrones de diseños aplicados (estructural): Patron_Adapter.png
-Patrones de diseños aplicados (comportamiento):
-Diseño de proceso en BPMN: BPMN_Diagram.png
-Explicaciones de diagramas y descripción de seguridad básica: Entrega2Grupo5.pdf 



## Instrucciones y Configuración

### 1. Crea un entorno virtual
```bash
python3 -m venv env
source env/bin/activate
```
## #2. Instala Dependencias
```bash
pip install -r requirements.txt
```
### 3. Inicializa y pobla la base de datos
```bash
make reset-db
```
### 4. Crear un administrador
```bash
make admin
```
### 5.Levantar el servidor
```bash
make run
```
El sistema estará disponible en: http://127.0.0.1:8000/
El panel de administración en: http://127.0.0.1:8000/admin/
