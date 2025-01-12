# Documentación del CI/CD Pipeline del Proyecto

Este documento describe el flujo de trabajo automatizado del pipeline de CI/CD, incluyendo un diagrama en **Mermaid**, una explicación detallada de cada parte, su ubicación en el repositorio y algunos consejos útiles.

---

## **1. Diagrama del Workflow**

Aquí se muestra el diagrama del flujo de trabajo:

```mermaid
flowchart TD
    subgraph Pipeline
        A[Push/Pull Request a Main] --> B[Setup Deploy]
        B --> C[Checkout del Repositorio]
        C --> D[Configurar Python 3.9]
        D --> E[Instalar Dependencias]
        E --> F[Configurar Credenciales AWS]
        F --> G[Ejecutar Deployment Script]
        G --> H[Extraer URL del Load Balancer]
        H --> I{¿Se detectó URL?}
        I --> |No| N[Fallo del Workflow]
        I --> |Sí| J[Continuar con Pruebas]
    end

    subgraph Pruebas
        J --> K[Esperar 2 Minutos]
        K --> L[Configuración Locust]
        L --> M[Ejecutar Pruebas de Carga]
        M --> O{¿Se Generó locust_result.html?}
        O --> |No| P[Fallo del Workflow]
        O --> |Sí| Q[Subir Resultados a S3]
    end

    Q --> R[Fin del Pipeline]
```

---

## **2. Explicación del Diagrama**

Este diagrama ilustra el flujo completo del pipeline de CI/CD descrito en el archivo `ci_cd_pipeline.yml`.

### **Etapas del Pipeline:**

1. **Inicio:** Se activa cuando se realiza un **push**, un **pull request** a la rama `notmain` o mediante una ejecución manual (`workflow_dispatch`).

2. **Setup Deploy (Despliegue):** 
   - Se realizan los siguientes pasos:
     - `Checkout del Repositorio`: Clona el repositorio en la máquina virtual (`actions/checkout@v4`).
     - `Configurar Python`: Instala y configura Python 3.9 (`actions/setup-python@v4`).
     - `Instalar Dependencias`: Instala `boto3`, `Flask`, `awscli`, etc., necesarias para ejecutar `deployment.py`.
     - `Configurar Credenciales AWS`: Autentica con los secretos de AWS.
     - `Ejecutar Script de Despliegue`: Despliega la aplicación en AWS EC2 mediante `src/deployment.py`.
     - `Extraer URL del Load Balancer`: Se extrae la URL del Load Balancer de la salida del script.

   **Validación de URL:** 
   - Si no se detecta una URL válida, el workflow falla con un mensaje de error. Esta URL es necesaria para las pruebas con locust
   - Si la URL es correcta, continúa con la etapa de pruebas. 

3. **Pruebas de Carga (`performance`):**
   - **Tiempo de espera:** Se espera 2 minutos (`sleep 120`) para garantizar que el Load Balancer esté listo.
   - **Configuración de Locust:** Se instala Locust para realizar la prueba de carga.
   - **Prueba de Carga:** Se simulan 1000 usuarios concurrentes, agregando 20 usuarios por segundo, durante 1 minuto.
   - **Validación del Reporte:** Si no se genera `locust_result.html`, el workflow falla con un error. Si se genera, sube el archivo al bucket S3.

4. **Subida de Resultados a S3:**
   - Verifica si el bucket `performance-reports-bucket` existe. Si no, lo crea.
   - Sube el archivo `locust_result.html` al bucket.

5. **Finalización del Pipeline:**
   - Si todos los pasos se completan correctamente, el pipeline finaliza con éxito.

---

## **3. Ubicación del Archivo workflow**

El archivo `ci_cd_pipeline.yml` que se documenta, se ubica en la carpeta `.github/workflows/` dentro del repositorio. 

---

## **4. Consejos Adicionales**
   
1. **Enlace en el `README.md`:** Puedes agregar un enlace al archivo de documentación desde el `README.md`:
   ```markdown
   [Ver la Documentación del programa y pasos para su ejecucion(./readme.md)
   ```

2. **Uso de Variables de Entorno:** 
   - Las credenciales AWS seguras deben situarse en los `secrets` de GitHub.
   - ¡No almacenes información sensible directamente en el archivo YAML!
