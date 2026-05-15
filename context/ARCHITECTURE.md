# ARCHITECTURE.md -- Tablero Kanban Personal con Límite WIP

## 1. Principio rector
El dominio no conoce Flask, HTTP, JSON, archivos, rutas, HTML, JavaScript, variables de entorno ni detalles de interfaz.

## 2. Estilo arquitectónico
Arquitectura Hexagonal con tres zonas principales:
- dominio: entidades, aggregate root, errores, invariantes y reglas de negocio.
- aplicacion: casos de uso y puertos abstractos.
- infraestructura: adaptadores HTTP, persistencia JSON y frontend.

## 3. Reglas de dependencia
- src/dominio/ no importa src/aplicacion/ ni src/infraestructura/.
- src/aplicacion/ puede importar src/dominio/.
- src/infraestructura/ puede importar src/aplicacion/ y src/dominio/.
- Las dependencias siempre apuntan hacia el núcleo, no hacia afuera.

## 4. Puerto de persistencia
La capa de aplicación define el puerto RepositorioTablero:
- RepositorioTablero.cargar() -> Tablero
- RepositorioTablero.guardar(tablero: Tablero) -> None

## 5. Adaptadores permitidos
- Adaptador de persistencia JSON en src/infraestructura/persistencia/.
- Adaptador HTTP Flask en src/infraestructura/http/.
- Frontend HTML/CSS/JavaScript en src/infraestructura/frontend/.

## 6. Verificación arquitectónica mínima
PowerShell:
```powershell
Get-ChildItem .\src\dominio -Recurse -Filter *.py | Select-String -Pattern "flask|json|requests|sqlalchemy|http"
```

Bash o Git Bash:
```bash
grep -R "flask\|json\|requests\|sqlalchemy\|http" src/dominio || true
```

La verificación aprueba cuando no aparecen importaciones prohibidas en src/dominio/.
