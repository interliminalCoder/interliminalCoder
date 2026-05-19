# Documentación del perfil

## Estructura del proyecto

```
├── README.md                       # Perfil de GitHub (se actualiza automáticamente)
├── src/
│   ├── fetch_activity.py           # Obtiene actividad reciente de GitHub
│   └── fetch_tidal.py              # Obtiene últimas canciones vía Last.fm
└── .github/workflows/
    ├── main.yml                    # Metrics con lowlighter/metrics (existente)
    └── update-profile.yml          # Ejecuta ambos scripts cada hora
```

## Scripts

### `src/fetch_activity.py`

- **Qué hace**: Consulta la API REST de GitHub (`/users/interliminalCoder/events/public`) y obtiene las últimas 10 acciones públicas.
- **Soporta**: Push, Issues, PRs, forks, stars, releases, wiki, etc.
- **Output**: Reemplaza el bloque `<!-- ACTIVITY:start --> ... <!-- ACTIVITY:end -->` en el README con una lista formateada.
- **Env var**: `GH_TOKEN` (opcional, mejora rate limit; el Action usa `${{ secrets.GITHUB_TOKEN }}`).

### `src/fetch_tidal.py`

- **Qué hace**: Consulta la API de Last.fm (`user.getrecenttracks`) y obtiene las últimas 5 canciones escuchadas.
- **Output**: Reemplaza el bloque `<!-- TIDAL:start --> ... <!-- TIDAL:end -->` en el README. Si hay una canción sonando ahora, la marca con ▶️.
- **Env vars**:
  - `LASTFM_API_KEY` (requerido)
  - `LASTFM_USER` (default: `intercoder`)

## GitHub Action (`.github/workflows/update-profile.yml`)

- **Schedule**: Cada hora (`0 * * * *`)
- **Trigger manual**: Desde la pestaña Actions del repo
- **Trigger en push**: También se ejecuta al hacer push a main/master
- **Flujo**:
  1. Checkout del repo
  2. Setup Python 3.12
  3. Ejecuta `fetch_activity.py`
  4. Ejecuta `fetch_tidal.py`
  5. Si README.md cambió, hace commit y push automático

## Secrets necesarios en GitHub

| Secret | Valor | ¿Dónde se configura? |
|---|---|---|
| `METRICS_TOKEN` | Token de GitHub con repo scope | `Settings > Secrets > Actions` (ya existente) |
| `LASTFM_API_KEY` | `8d16339a641adcd374248aa7becd542d` | `Settings > Secrets > Actions` |
| `LASTFM_USER` | `intercoder` | `Settings > Secrets > Actions` |

Los secrets del Action `update-profile.yml` usan `GITHUB_TOKEN` automático (no necesita configurarse).

## Cómo ejecutar manualmente

1. Ir a https://github.com/interliminalCoder/interliminalCoder/actions
2. Seleccionar "Update Profile"
3. Click "Run workflow" → "Run workflow"

## Para añadir un nuevo script

1. Crear el script en `src/`
2. Usar `<!-- NOMBRE:start --> ... <!-- NOMBRE:end -->` en README.md
3. Añadir el step en `.github/workflows/update-profile.yml`
4. Si necesita API key, agregarla como secret en GitHub
