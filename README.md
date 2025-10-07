# Sistema de Búsqueda y Gestión de Álbumes Musicales

## Narrativa del Proyecto

Este proyecto es una aplicación web desarrollada con **Django** que permite a los usuarios buscar información detallada sobre álbumes musicales utilizando **APIs externas**.  
El sistema ofrece funcionalidades de **gestión de usuarios**, **historial de búsquedas** y una **lista personalizada de "escuchar más tarde"** para que los usuarios puedan organizar y gestionar su experiencia musical.

La aplicación surge de la necesidad de centralizar la búsqueda de información musical, proporcionando una interfaz intuitiva que permita a los usuarios encontrar álbumes, explorar su información detallada y mantener un registro personalizado de su actividad musical.

---

## Abstract

El Sistema de Búsqueda y Gestión de Álbumes Musicales es una aplicación web que integra servicios de búsqueda musical con funcionalidades de gestión personal.  
Desarrollado con **Django** y utilizando **APIs externas** para obtener información musical, el sistema permite realizar búsquedas avanzadas de álbumes, mantener un historial de consultas y gestionar listas personalizadas de reproducción futura.  
La plataforma incluye un sistema completo de **autenticación de usuarios** y proporciona una experiencia personalizada para cada usuario registrado.

---

## Requerimientos Funcionales

### RF001 - Gestión de Usuarios
- El sistema debe permitir el registro de nuevos usuarios  
- El sistema debe permitir el inicio de sesión con credenciales válidas  
- El sistema debe permitir el cierre de sesión seguro  
- El sistema debe mantener sesiones activas de usuarios autenticados  

### RF002 - Búsqueda de Álbumes
- El sistema debe permitir buscar álbumes por nombre  
- El sistema debe mostrar resultados detallados de búsqueda  
- El sistema debe ignorar los álbumes guardados en la lista “Escuchar más tarde”  
- El sistema debe integrar con APIs externas para obtener información musical  
- El sistema debe mostrar información como título, artista, año, género, etc.  

### RF003 - Historial de Búsquedas
- El sistema debe registrar automáticamente las búsquedas de usuarios autenticados  
- El sistema debe permitir visualizar el historial de búsquedas personal  
- El sistema debe permitir eliminar entradas específicas del historial  
- El sistema debe asociar cada búsqueda con el usuario que la realizó  

### RF004 - Lista "Escuchar Más Tarde"
- El sistema debe permitir agregar álbumes a una lista personal  
- El sistema debe permitir eliminar álbumes de la lista personal  
- El sistema debe permitir marcar álbumes como "escuchados" o "no escuchados"  
- El sistema debe mostrar el estado actual de cada álbum en la lista  

### RF005 - Interfaz de Usuario
- El sistema debe proporcionar una interfaz web responsiva  
- El sistema debe mostrar resultados de búsqueda de forma clara y organizada  
- El sistema debe proporcionar navegación intuitiva entre funcionalidades  

---

## Requerimientos No Funcionales

### RNF001 - Seguridad
- Autenticación segura de usuarios  
- Contraseñas encriptadas en la base de datos  
- Prevención de inyección SQL  
- Sesiones con tiempo de expiración configurado  

### RNF002 - Usabilidad
- Interfaz intuitiva y fácil de usar  
- Mensajes de error claros  
- Navegación consistente en toda la aplicación  

### RNF003 - Disponibilidad
- Alta disponibilidad del sistema  
- Manejo de errores de APIs externas  
- Mensajes informativos cuando los servicios externos no estén disponibles  

### RNF004 - Compatibilidad
- Funcionamiento en navegadores modernos (Chrome, Firefox, Safari, Edge)

---

## Stack Tecnológico

### Backend
- **Framework:** Django 4.x (Python)  
- **Base de Datos:** PostgreSQL  
- **ORM:** Django ORM  
- **Autenticación:** Django Authentication System  

### Frontend
- **Templates:** Django Templates  
- **CSS:** CSS personalizado  
- **JavaScript:** Vanilla JS  

### Infraestructura
- **Contenedor:** Docker  
- **Control de Versiones:** Git  

### APIs Externas
- **Fuente de datos:** Discogs API (álbumes musicales)  
- **Editor:** Visual Studio Code  
- **Gestor de dependencias:** pip + `requirements.txt`  
- **Variables de entorno:** `python-decouple`  
- **Migraciones:** Django Migrations  

---

## Reglas de Negocio

### RN001 - Autenticación
- Solo usuarios registrados pueden acceder a historial y listas personales  
- Los usuarios no autenticados no pueden realizar búsquedas  
- Las sesiones expiran automáticamente  

### RN002 - Búsquedas
- Se registran en un historial personal  
- Las búsquedas vacías no se procesan  
- Se limita la cantidad de búsquedas por usuario para prevenir abuso  

### RN003 - Historial
- Cada usuario solo puede ver y gestionar su propio historial  
- Se pueden eliminar entradas individuales  
- El historial tiene un límite máximo por usuario  

### RN004 - Lista "Escuchar Más Tarde"
- Lista personal única por usuario  
- No se permiten álbumes duplicados  
- Estados posibles: "por escuchar" y "escuchado"  

### RN005 - Datos
- Información obtenida en tiempo real desde APIs externas  
- Datos personales (historial, listas) almacenados localmente  
- Integridad referencial entre usuarios y sus datos  

---

## Casos de Uso Principales

### CU001 - Registrar Usuario
**Actor:** Usuario no registrado  
**Flujo Principal:**
1. Accede a la página de registro  
2. Completa el formulario con datos válidos  
3. El sistema valida y crea la cuenta  
4. El usuario es autenticado y redirigido a la página principal  

### CU002 - Buscar Álbum
**Actor:** Usuario autenticado  
**Flujo Principal:**
1. Ingresa el nombre del álbum  
2. Envía la búsqueda  
3. El sistema consulta APIs externas  
4. Se muestran los resultados y se registra la búsqueda  

### CU003 - Gestionar Lista "Escuchar Más Tarde"
**Actor:** Usuario autenticado  
**Flujo Principal:**
1. Busca un álbum  
2. Selecciona “Agregar a Escuchar Más Tarde”  
3. El sistema agrega el álbum a la lista  
4. El usuario puede marcar álbumes como escuchados o eliminarlos  

### CU004 - Consultar Historial
**Actor:** Usuario autenticado  
**Flujo Principal:**
1. Accede a su historial  
2. Visualiza las búsquedas  
3. Elimina entradas específicas  

---

## Modelo de Dominio
![Diagrama clases tpi soporte](https://github.com/user-attachments/assets/ce7d4c47-85cc-45d2-8216-6e4fb38463af)


---

## Documentación de Librerías

- [Django](https://docs.djangoproject.com/en/5.2/)  
- [PostgreSQL](https://www.postgresql.org/docs/)  
- [Docker](https://docs.docker.com/)

