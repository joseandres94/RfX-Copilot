# Alembic Migrations

Este directorio contiene las migraciones de base de datos gestionadas por Alembic.

## Estructura

```
backend/alembic/
├── alembic.ini          # Configuración principal (en backend/)
├── env.py               # Configuración del entorno de migraciones
├── script.py.mako        # Plantilla para nuevas migraciones
└── versions/             # Archivos de migración (uno por cambio)
    ├── 001_initial.py
    ├── 002_add_index.py
    └── ...
```

## Uso

### Desde el directorio raíz del proyecto:

```bash
# Crear nueva migración
alembic -c backend/alembic.ini revision --autogenerate -m "Descripción"

# Aplicar migraciones
alembic -c backend/alembic.ini upgrade head

# Ver estado actual
alembic -c backend/alembic.ini current
```

### Usando el script helper:

```bash
# Crear nueva migración
python scripts/migrate.py revision --autogenerate -m "Descripción"

# Aplicar migraciones
python scripts/migrate.py upgrade head

# Ver estado actual
python scripts/migrate.py current
```

## Notas Importantes

- **SQLite Async**: Alembic usa un motor síncrono para las migraciones, aunque la aplicación use async.
  Esto es normal y necesario para que Alembic funcione correctamente con SQLite.

- **Modelos**: Todos los modelos deben estar importados en `env.py` para que Alembic los detecte.

- **Versiones**: Las migraciones se guardan en `versions/` y deben estar versionadas en Git.

## Más Información

- Ver `MIGRATION_USAGE.md` en la raíz del proyecto para documentación completa.
- Ver `DATABASE_MIGRATION_GUIDE.md` para explicación detallada de las opciones.

