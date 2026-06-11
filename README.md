# fspy-rhino

Importador de cámara [fSpy](https://fspy.io/) para **Rhino** y **Grasshopper**. Lee el JSON exportado por fSpy y aplica posición, orientación, FOV e imagen de referencia en el viewport o en el modelo 3D.

## Requisitos

- Rhino 6 / 7 / 8 con Grasshopper
- GhPython (incluido en Rhino 6+)

## Inicio rápido

1. En fSpy: calibra la cámara y exporta **File → Export → Camera parameters as JSON**.
2. En Grasshopper: añade un componente **Python** y pega el contenido de `fSpy_Import_Camera.ghpy`.
3. Crea las entradas: `json_path_or_string`, `Apply`, `image_path` (opcional), `BakeImage` (opcional).
4. Crea las salidas: `CameraLocation`, `CameraTarget`, `CameraUp`, `FOV_h_deg`, `FOV_v_deg`, `ImageW`, `ImageH`, `PrincipalPoint`, `Applied`, `ImageCorners`, `ImageContour`, `ImageSurface`, `Error`.
5. Conecta un **Panel** con la ruta al `.json` (usa `/` en lugar de `\` en Windows si hay problemas).

## Archivos

| Archivo | Descripción |
|--------|-------------|
| `fSpy_Import_Camera.ghpy` | **Recomendado.** Componente todo-en-uno: parsea JSON, aplica cámara, imagen de fondo y bake. |
| `fSpy_Parse_JSON.ghpy` | Solo lee el JSON y devuelve parámetros de cámara. |
| `fSpy_Apply_To_View.ghpy` | Solo aplica la cámara al viewport activo. |
| `fspy_camera_utils.py` | Módulo auxiliar (opcional; el script principal es autocontenido). |

## Entradas (`fSpy_Import_Camera`)

| Entrada | Descripción |
|--------|-------------|
| `json_path_or_string` | Ruta al `.json` de fSpy o el JSON como texto |
| `Apply` | `True` = aplicar cámara al viewport activo |
| `image_path` | Ruta a la misma imagen usada en fSpy (fondo alineado) |
| `BakeImage` | `True` = insertar la imagen en el documento como PictureFrame |

## Salidas (`fSpy_Import_Camera`)

| Salida | Descripción |
|--------|-------------|
| `CameraLocation` | Posición de la cámara (Point3d) |
| `CameraTarget` | Centro del plano de imagen / punto al que mira la cámara |
| `CameraUp` | Vector arriba de la cámara |
| `FOV_h_deg` / `FOV_v_deg` | Campo visual horizontal / vertical (grados) |
| `ImageW` / `ImageH` | Dimensiones de la imagen (píxeles) |
| `PrincipalPoint` | Punto principal de fSpy |
| `Applied` | `True` si la cámara se aplicó al viewport |
| `ImageCorners` | 4 esquinas del marco de imagen en 3D |
| `ImageContour` | Curva cerrada del borde de la imagen |
| `ImageSurface` | Superficie rectangular (para bake de geometría) |
| `Error` | Mensaje de error, si lo hay |

> Quita la salida **Out** por defecto del componente Python. La que dice "standard output" es para mensajes, no para la posición de cámara.

## Flujo (como en fSpy)

1. Viewport con relación de aspecto = `ImageW` / `ImageH`
2. Imagen como fondo (`image_path` + `Apply`) o en el modelo (`BakeImage`)
3. Campo visual (FOV)
4. Posición y orientación de cámara
5. Punto principal (si no está en el centro, la imagen puede verse corrida respecto al recuadro)

## Solución de problemas

### Python 3.9 no inicializa en Grasshopper

Espera la primera descarga del runtime, reinicia Rhino o usa el componente **Python Script** (IronPython). Ver [Rhino – Scripting Languages Initialization](https://developer.rhino3d.com/guides/scripting/advanced-langinit/).

### `CameraLocation` vacío

Conecta un Panel con la ruta al JSON en `json_path_or_string`. Revisa la salida `Error`.

### Imagen corrida respecto al recuadro

Suele deberse al **principal point** en fSpy. Exporta con el punto principal en el centro de la imagen.

## Licencia

Scripts compatibles con el uso de [fSpy](https://github.com/stuffmatic/fSpy) (GPL). fSpy es software de [stuffmatic](https://fspy.io/).
