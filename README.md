# Sistema de Búsqueda y Gestión de Álbumes Musicales

## Narrativa del Proyecto

Este proyecto es una aplicación web desarrollada con **Django** que permite a los usuarios buscar información detallada sobre álbumes musicales utilizando **APIs externas**.  
El sistema ofrece funcionalidades de **gestión de usuarios**, **historial de búsquedas** y una **lista personalizada de "escuchar más tarde"** para que los usuarios puedan organizar y gestionar su experiencia musical.

Se incorpora inteligencia artificial para enriquecer la experiencia del usuario mediante la generación automática de descripciones de álbumes, proporcionando contexto adicional sobre los artistas, el estilo musical y la importancia cultural de cada álbum.

La aplicación surge de la necesidad de centralizar la búsqueda de información musical, proporcionando una interfaz intuitiva que permita a los usuarios encontrar álbumes, explorar su información detallada y mantener un registro personalizado de su actividad musical.

---

## Abstract

Album Recommender es una aplicación web que integra servicios de búsqueda musical con funcionalidades de gestión personal.  
Desarrollado con **Django** y utilizando **APIs externas** para obtener información musical, el sistema permite realizar búsquedas avanzadas de álbumes, mantener un historial de consultas y gestionar listas personalizadas de reproducción futura.  
La plataforma incluye un sistema completo de **autenticación de usuarios** y proporciona una experiencia personalizada para cada usuario registrado.

---

## Requerimientos Funcionales

### RF001 - Gestión de Usuarios
- El sistema debe permitir el registro de nuevos usuarios  
- El sistema debe permitir el inicio de sesión con credenciales válidas  
- El sistema debe permitir el cierre de sesión seguro  
- El sistema debe mantener sesiones activas de usuarios autenticados
- El sistema debe permitir la actualización de foto de perfil

### RF002 - Búsqueda de Álbumes
- El sistema debe permitir buscar álbumes por nombre  
- El sistema debe mostrar resultados detallados de búsqueda  
- El sistema debe ignorar los álbumes guardados en la lista “Escuchar más tarde”  
- El sistema debe integrar con APIs externas para obtener información musical
- El sistema debe generar descripciones inteligentes de álbumes bajo demanda usando OpenAI GPT
- El sistema debe validar si existe información suficiente antes de generar descripciones con IA
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
- El sistema debe permitir generar descripciones con IA directamente desde la lista personal

### RF005 - Interfaz de Usuario
- El sistema debe proporcionar una interfaz web responsiva  
- El sistema debe mostrar resultados de búsqueda de forma clara y organizada  
- El sistema debe proporcionar navegación intuitiva entre funcionalidades

### RF005 - Inteligencia Artificial
- El sistema debe integrar con OpenAI API para generación de descripciones
- El sistema debe construir prompts contextualizados usando metadatos del álbum
- El sistema debe manejar casos donde no existe información suficiente del álbum
- El sistema debe generar descripciones de 2-3 oraciones enfocadas en género, estilo, temas y recepción
- El sistema debe responder de forma asíncrona sin bloquear la interfaz
- El sistema no debe almacenar las descripciones generadas (stateless)

---

## Requerimientos No Funcionales

### RNF001 - Seguridad
- Autenticación segura de usuarios  
- Contraseñas encriptadas en la base de datos  
- Prevención de inyección SQL  
- Sesiones con tiempo de expiración configurado
- Protección de API keys mediante variables de entorno

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
- **Procesamiento de Imágenes:** Pillow 10.1.0
- **Inteligencia Artificial:** OpenAI Python SDK 1.50.0+


### Frontend
- **Templates:** Django Templates  
- **CSS:** CSS personalizado  
- **JavaScript:** Vanilla JS  

### Infraestructura
- **Contenedor:** Docker  
- **Control de Versiones:** Git
- **Base de Datos:** PostgreSQL (containerizada)

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
- Enriquecimiento de álbumes se ejecuta de forma asíncrona en segundo plano
- Álbumes se marcan como enriquecidos (is_enriched=True) tras completar el proceso

### RN006 - Inteligencia Artificial
- Las descripciones generadas por IA son stateless (no se almacenan)
- Se requiere al menos el título del álbum para generar descripciones
- Si no existe información suficiente, el modelo responde con "NO_INFO"
- Las descripciones deben ser concisas (2-3 oraciones)
- Se debe informar al usuario cuando la IA no tiene información específica del álbum
- El sistema debe manejar errores de OpenAI API de forma transparente

### RN007 - Recomendaciones
- Se priorizan álbumes con rating ≥ 3.5 y ≥ 20 valoraciones
- Se excluyen álbumes del mismo artista principal
- Se evitan artistas repetidos en recomendaciones
- Se buscan hasta 3 recomendaciones por consulta
- Búsqueda por estilos tiene prioridad sobre búsqueda por género

---

## Casos de Uso Principales

### CU001 - Registrar Usuario
**Actor:** Usuario no registrado  
**Flujo Principal:**
1. Accede a la página de registro
2. Completa el formulario con email, username y contraseñas
3. El sistema valida unicidad de email y username
4. El sistema crea la cuenta y autentica automáticamente
5. El usuario es redirigido a la página principal de búsqueda

### CU002 - Buscar Álbum con Recomendaciones
**Actor:** Usuario autenticado  
**Flujo Principal:**
1. Ingresa el nombre del álbum en la página de búsqueda
2. El sistema muestra pantalla de carga
3. El sistema consulta la API de Discogs
4. El sistema filtra álbumes ya en "Escuchar más tarde"
5. El sistema genera recomendaciones basadas en género/estilo del álbum principal
6. Se muestran los resultados de búsqueda
7. La búsqueda se registra automáticamente en el historial

### CU003 - Generar Descripción con IA
**Actor:** Usuario autenticado  
**Flujo Principal:**
1. Usuario visualiza un álbum en resultados o lista personal
2. Usuario hace clic en botón "AI Description"
3. El sistema envía petición al endpoint de descripción
4. El backend construye un prompt contextualizado con metadatos del álbum
5. El sistema llama a la API de OpenAI
6. OpenAI genera descripción o responde "NO_INFO"
7. El sistema retorna JSON con información de disponibilidad y descripción
8. La interfaz muestra la descripción sin recargar la página

**Flujos Alternativos:**
- **3a.** Si OpenAI API no está disponible: Se muestra mensaje de error 
- **5a.** Si el modelo no tiene información: Se muestra mensaje indicando falta de información

### CU004 - Gestionar Lista "Escuchar Más Tarde"
**Actor:** Usuario autenticado  
**Flujo Principal:**
1. Busca un álbum en resultados
2. Selecciona "Add to Listen Later"
3. El sistema crea o recupera el álbum en la base de datos
4. Si es nuevo, se dispara enriquecimiento asíncrono de datos
5. El sistema crea un registro de favorito con tipo 'listen_later'
6. El usuario puede visualizar su lista personal
7. El usuario puede marcar álbumes como escuchados/no escuchados
8. El usuario puede generar descripciones con IA desde la lista
9. El usuario puede eliminar álbumes de la lista


---

## Modelo de Dominio
![Diagrama clases tpi soporte](https://github.com/user-attachments/assets/ce7d4c47-85cc-45d2-8216-6e4fb38463af)


---

## Documentación de Librerías

- [Django](https://docs.djangoproject.com/en/5.2/)  
- [PostgreSQL](https://www.postgresql.org/docs/)  
- [Docker](https://docs.docker.com/)


