-- Script de creación de tablas de ejemplo
-- Modifica según las necesidades de tu proyecto

-- Ejemplo de tabla
CREATE TABLE Ejemplo (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(100) NOT NULL,
    Descripcion NVARCHAR(500),
    FechaCreacion DATETIME DEFAULT GETDATE(),
    Activo BIT DEFAULT 1
);

-- Agrega más tablas según tu proyecto de bases de datos distribuidas
