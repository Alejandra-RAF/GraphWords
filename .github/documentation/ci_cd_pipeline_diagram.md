# Documentación del CI/CD Pipeline del Proyecto

Este archivo describe el flujo de trabajo automatizado del pipeline de CI/CD, mostrando un diagrama en **Mermaid** y explicando cada parte del proceso.

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
        M --> N{¿Se Generó locust_result.html?}
        N --> |No| O[Fallo del Workflow]
        N --> |Sí| P[Subir Resultados a S3]
    end

    P --> Q[Fin del Pipeline]
