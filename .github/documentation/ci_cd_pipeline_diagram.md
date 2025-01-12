# Diagrama del CI/CD Pipeline del Proyecto

Este documento muestra el flujo de trabajo del archivo `ci_cd_pipeline.yml`.

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
    end

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
