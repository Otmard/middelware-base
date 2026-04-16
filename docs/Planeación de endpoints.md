# Planeación de Endpoints

## Endpoint: Consulta de Cliente

```http
POST /api/consulta-cliente
```

### Descripción

Este servicio permite consultar información de un cliente mediante un código de búsqueda, retornando sus datos personales y detalle de deuda (facturas o periodos).

---

## Solicitud

### Headers

| Parámetro  | Descripción                       | Tipo   | Obligatorio |
| ---------- | --------------------------------- | ------ | ----------- |
| Entidad    | Identificador de la entidad (BCP) | String | Sí         |
| Usuario    | Usuario autorizado                | String | Sí         |
| Contraseña | Credenciales de acceso            | String | Sí         |

### Body (CargaUtil)

| Parámetro        | Descripción               | Tipo   | Tamaño |
| ---------------- | ------------------------- | ------ | ------ |
| CodServicio      | Código del servicio       | String | 3      |
| CodigoBusqueda   | Código único del cliente  | String | 14     |

### Ejemplo de Solicitud

```json
{
  "Cabecera": {
    "Entidad": "BCP",
    "Usuario": "USUARIO_AUTORIZADO",
    "Contraseña": "********"
  },
  "CargaUtil": {
    "CodServicio": "001",
    "CodigoBusqueda": "CLIE12345"
  }
}
```

---

## Respuesta

### Headers de Respuesta

| Parámetro   | Descripción                                      | Tipo   | Tamaño |
| ----------- | ------------------------------------------------ | ------ | ------ |
| CodError    | Código de respuesta. "000" indica éxito.         | String | 3      |
| Descripcion | Mensaje descriptivo del código de error.         | String | 100    |

### Léxico de Códigos de Error

| Código | Descripción                          |
| ------ | ------------------------------------ |
| 000    | Proceso conforme                    |
| 100    | Error de autenticación              |
| 200    | Parámetros inválidos                |
| 301    | Código de depositante no existe     |
| 999    | Error interno del servidor          |

### Body de Respuesta (CargaUtil)

| Parámetro          | Descripción                                        | Tipo       | Tamaño | Observaciones                          |
| ------------------ | -------------------------------------------------- | ---------- | ------ | -------------------------------------- |
| CodigoBusqueda     | Código del cliente                                | String     | 14     | Debe coincidir con la consulta         |
| CodigoServicio     | Código del servicio                               | String     | 3      | Proporcionado por BCP                  |
| ImporteAdeudado    | Total de la deuda (suma de facturas/periodos)     | Decimal    | 9,2    | 0 si se maneja solo con detalle        |
| ImporteMinimo      | Importe mínimo total a pagar                      | Decimal    | 9,2    | Según reglas del servicio              |
| ImporteComision    | Comisión                                          | Decimal    | 9,2    | Enviar 0                               |
| NombreCliente      | Nombre del cliente                                | String     | 40     | -                                      |
| Pagos              | Lista de facturas o periodos                      | List<Pagos> | -     | Ver detalle en sección siguiente        |

---

## Estructura Pagos

| Parámetro          | Descripción                    | Tipo   | Formato/Observaciones       |
| ------------------ | ------------------------------ | ------ | --------------------------- |
| NumeroCuota        | ID del periodo/factura         | int    | Correlativo                 |
| DetalleCuota       | Descripción                   | string | Ej: "Factura Enero 2026"   |
| FechaVencimiento   | Fecha límite de pago          | string | Formato: AAAAMMDD           |
| ImporteCuota       | Monto total de la cuota        | decimal| -                           |
| ImporteMinimoCuota | Monto mínimo a pagar           | decimal| -                           |
| MoraCuota          | Monto de mora aplicado        | decimal| -                           |
| ImporteComision    | Comisión por cuota             | decimal| Enviar 0                    |

---

## Ejemplos de Respuesta

### Caso 1: Respuesta Fallida

Se presenta cuando la consulta no puede procesarse (cliente no existe, código inválido, error de validación).

**Condiciones:**
- `CodError` ≠ "000"
- `Pagos` = lista vacía
- `ImporteAdeudado` = 0.00

```json
{
  "Headers": {
    "CodError": "301",
    "Descripcion": "CÓDIGO DE DEPOSITANTE NO EXISTE"
  },
  "CargaUtil": {
    "CodigoBusqueda": "CLIE12345",
    "CodigoServicio": "001",
    "ImporteAdeudado": 0.00,
    "ImporteMinimo": 0.00,
    "ImporteComision": 0.00,
    "NombreCliente": "",
    "Pagos": []
  }
}
```

---

### Caso 2: Éxito sin Detalle (Deuda Única)

Se presenta cuando el cliente existe y la deuda se maneja como un único monto total, sin necesidad de mostrar facturas o periodos.

**Condiciones:**
- `CodError` = "000"
- `Pagos` = lista vacía
- `ImporteAdeudado` > 0

```json
{
  "Headers": {
    "CodError": "000",
    "Descripcion": "PROCESO CONFORME"
  },
  "CargaUtil": {
    "CodigoBusqueda": "CLIE12345",
    "CodigoServicio": "001",
    "ImporteAdeudado": 300.00,
    "ImporteMinimo": 0.00,
    "ImporteComision": 0.00,
    "NombreCliente": "PABLO PEREZ GUERRA",
    "Pagos": []
  }
}
```

---

### Caso 3: Éxito con Detalle de Facturas/Periodos

Se presenta cuando el cliente existe y la deuda está compuesta por múltiples facturas o periodos.

**Condiciones:**
- `CodError` = "000"
- `Pagos` = lista con datos
- `ImporteAdeudado` puede ser la suma total o 0 (según política del servicio)

```json
{
  "Headers": {
    "CodError": "000",
    "Descripcion": "PROCESO CONFORME"
  },
  "CargaUtil": {
    "CodigoBusqueda": "CLIE12345",
    "CodigoServicio": "002",
    "ImporteAdeudado": 2250.00,
    "ImporteMinimo": 0.00,
    "ImporteComision": 0.00,
    "NombreCliente": "PABLO PEREZ GUERRA",
    "Pagos": [
      {
        "NumeroCuota": 1,
        "DetalleCuota": "Factura Enero 2026",
        "FechaVencimiento": "20260131",
        "ImporteCuota": 750.00,
        "ImporteMinimoCuota": 0.00,
        "MoraCuota": 50.00,
        "ImporteComision": 0.00
      },
      {
        "NumeroCuota": 2,
        "DetalleCuota": "Factura Febrero 2026",
        "FechaVencimiento": "20260228",
        "ImporteCuota": 750.00,
        "ImporteMinimoCuota": 0.00,
        "MoraCuota": 0.00,
        "ImporteComision": 0.00
      }
    ]
  }
}
```

---

## Resumen de Casos

| Caso                 | CodError | Pagos     | ImporteAdeudado | Interpretación          |
| -------------------- | -------- | --------- | --------------- | ----------------------- |
| Fallido              | ≠ "000"  | Vacío     | 0               | Error en consulta       |
| Éxito simple        | "000"    | Vacío     | > 0             | Deuda total única       |
| Éxito con detalle   | "000"    | Con datos | 0 o suma        | Facturas/periodos       |

---

## Notas de Implementación

1. **Autenticación**: Validar credenciales en cada solicitud.
2. **Límite de registros**: Si `Pagos` contiene muchos registros, considerar paginación.
3. **Moneda**: Asumir decimales con separador de punto (formato JSON estándar).
4. **Timezone**: Las fechas están en formato ISO (AAAAMMDD), sin hora.
