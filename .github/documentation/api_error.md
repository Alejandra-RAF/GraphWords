# Documentación del Flujo de Trabajo

Este repositorio ejecuta pruebas automáticas usando GitHub Actions.

```mermaid
graph TD
    A[Inicio: Push en main] --> B[GitHub Actions]
    B --> C[Checkout del código]
    C --> D[Configuración de Node.js]
    D --> E[Instalación de dependencias]
    E --> F[Ejecutar pruebas]
    F --> G[Fin]
