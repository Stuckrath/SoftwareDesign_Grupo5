# SoftwareDesign_Grupo5
Avances hechos para el trabajo semestral de Diseño de Software (501352), de parte del grupo 5


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