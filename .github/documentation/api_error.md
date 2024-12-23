# Documentación del Flujo de Trabajo

Este repositorio ejecuta pruebas automáticas usando GitHub Actions.

```mermaid
graph TD
    A[Push to Main Branch or Manual Trigger] --> B[Setup Environment]
    B -->|Install Dependencies| C[Run Deployment Script]
    C -->|Successful Execution| D[End Workflow]
    C -->|Failure| E[Notify Failure]
