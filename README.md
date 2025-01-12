# **GraphWord: Despliegue en AWS EC2 y Ejecución con GitHub Actions**

Este proyecto implementa una aplicación distribuida utilizando instancias **EC2**, un **balanceador de carga (ALB)** y buckets **S3** para almacenar los scripts y los datos generados. Este archivo explica cómo se estructura la memoria relacionada con AWS EC2 y cómo ejecutar el programa utilizando GitHub Actions para desplegarlo en la nube.

---

## **1. Arquitectura en AWS EC2**

La arquitectura se basa en una infraestructura distribuida con los siguientes componentes:

- **Instancias EC2:** Servidores virtuales que ejecutan los scripts de procesamiento.
- **Balanceador de Carga (ALB):** Distribuye el tráfico HTTP de manera equitativa entre las instancias EC2.
- **Buckets S3:** Almacenan los scripts necesarios y los datos generados por las instancias.
- **VPC:** Red privada virtual que abarca un rango de direcciones IP con subredes públicas.

### **Flujo del Despliegue:**
1. **Carga de scripts en S3:** Los scripts de Python son subidos al bucket `deployments-bucket456`.
2. **Creación de infraestructura:** Se crea la **VPC**, subredes, tablas de rutas y grupos de seguridad.
3. **Despliegue del Balanceador de Carga (ALB):** Configura el listener para enrutar tráfico HTTP al puerto 5000 de las instancias EC2.
4. **Lanzamiento de Instancias EC2:** Se ejecutan los scripts de inicio que descargan y procesan los datos.
5. **Consulta:** La API Flask devuelve los resultados, como rutas entre palabras, desde el endpoint público del ALB.

---

## **2. Configuración del Workflow de GitHub Actions**

Este proyecto incluye un archivo `ci_cd_pipeline.yml` que automatiza el despliegue y las pruebas mediante GitHub Actions. Tambien se incluye un archvio `ci_cd_documentation.md` que describe el workflow mediante un diagrama y texto.

---

## **3. Pasos para Ejecutar el Programa en la Nube**

### **1. Clonar el repositorio:**
```bash
git clone <URL_DEL_REPOSITORIO>
cd GraphWord
```

### **2. Configurar los secretos de GitHub:**
- Accede al repositorio en GitHub.
- Ve a **Settings > Secrets and Variables > Actions**.
- Agrega los siguientes secretos:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_SESSION_TOKEN`

En cada uno de ellos deberás de utilizar tus credenciales de AWS en donde quieras implementar la infraestructura del proyecto GraphWords.

### **3. Ejecutar el Workflow:**
- Ve a la pestaña **Actions** en GitHub.
- Selecciona el workflow **CI/CD Pipeline**.
- Haz click en **"Run workflow"** si deseas ejecutarlo manualmente (asegurate de seleccionar la rama **Main**).

---

## **4. Resultados del Despliegue**

- **Acceso a la API:** Una vez desplegado, puedes acceder a la API Flask mediante la URL proporcionada por el balanceador de carga (ALB).
- **Pruebas de Carga:** El workflow incluye pruebas de rendimiento con **Locust** para verificar la estabilidad de la API con usuarios concurrentes. Estos estaran subidos en el bucket creado automaticamente de `performance-reports-bucket` en el S3 de tu AWS.

---

## **Conclusión**

Este `README.md` proporciona una guía completa para desplegar la aplicación `GraphWords` en AWS EC2 mediante GitHub Actions. La combinación de **balanceador de carga**, **EC2** y **buckets S3** garantiza una infraestructura robusta y escalable.
