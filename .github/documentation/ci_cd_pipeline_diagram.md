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

        subgraph Pruebas
            H --> I[Esperar 2 Minutos]
            I --> J[Configuración Locust]
            J --> K[Ejecutar Pruebas de Carga]
            K --> L[Generar Archivo locust_result.html]
            L --> M[Subir Resultados a S3]
        end

        subgraph ErrorCheck
            K --> |Error: No se generó locust_result.html| N[Fallo del Workflow]
        end

        M --> O[Fin del Pipeline]
    end

---

### **Explicación del Diagrama:**

1. **Inicio:** Se activa cuando hay un **push/pull request** en la rama `main`.
2. **Setup Deploy:** 
   - **Pasos:**
     - `Checkout del repositorio`: Se clona el código.
     - `Configurar Python`: Se configura el entorno con Python 3.9.
     - `Instalación de dependencias`: Se instalan las librerías necesarias (`boto3`, `Flask`, `awscli`).
     - `Configurar credenciales AWS`: Se autentica con los secretos de AWS.
     - `Ejecutar script deployment.py`: Despliega la aplicación en AWS EC2.
     - `Extraer URL`: Se guarda la URL del Load Balancer para las pruebas.
3. **Pruebas de Carga:**
   - Se espera 2 minutos para que el entorno esté disponible.
   - Se ejecuta **Locust** con las pruebas de carga.
   - Si se genera el archivo `locust_result.html`, se sube a **S3**.
4. **Control de Errores:** 
   - Si el archivo de resultados no se genera, el workflow falla.
5. **Fin del Pipeline:** Si todo funciona, se cierra el pipeline exitosamente.

---

### **Visualización:**
Este diagrama refleja el flujo de cada paso en tu workflow YAML y es ideal para documentar cómo funciona tu CI/CD pipeline en GitHub. Puedes integrarlo en tu `README.md` o `DOCUMENTATION.md` con Mermaid para una vista gráfica más clara.
