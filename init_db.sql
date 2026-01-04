-- Elimina tablas si existen
DROP TABLE IF EXISTS incidencias;
DROP TABLE IF EXISTS usuarios_informatica;
DROP TABLE IF EXISTS usuarios_general;

-- Tabla de usuarios de informática
CREATE TABLE usuarios_informatica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Tabla de usuarios generales
CREATE TABLE usuarios_general (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    direccion_trabajo VARCHAR(150) NOT NULL
);

-- Tabla de incidencias
CREATE TABLE incidencias (
    id VARCHAR(8) PRIMARY KEY,
    resumen VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    servicio VARCHAR(50) NOT NULL,
    prioridad VARCHAR(20) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha_deseada DATE NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios_general(id)
);

-- ------------------- DATOS DE EJEMPLO -------------------

-- Usuarios de informática
INSERT INTO usuarios_informatica (usuario, password) VALUES
('admin', 'admin123'),
('tecnico1', 'clave123'),
('tecnico2', 'clave456');

-- Usuarios generales (30 ejemplos)
INSERT INTO usuarios_general (usuario, departamento, correo, nombre_completo, direccion_trabajo) VALUES
('jlopez', 'Control', 'jlopez@empresa.com', 'Juan López García', 'Despacho 4, Planta 5, Edificio Central'),
('mfernandez', 'Administración', 'mfernandez@empresa.com', 'María Fernández Ruiz', 'Despacho 2, Planta 3, Edificio Norte'),
('acastro', 'Recursos Humanos', 'acastro@empresa.com', 'Ana Castro Pérez', 'Despacho 7, Planta 2, Edificio Sur'),
('rnavarro', 'Finanzas', 'rnavarro@empresa.com', 'Raúl Navarro Díaz', 'Despacho 10, Planta 1, Edificio Este'),
('lmartin', 'Marketing', 'lmartin@empresa.com', 'Laura Martín Gómez', 'Despacho 12, Planta 4, Edificio Central'),
('jramirez', 'Ventas', 'jramirez@empresa.com', 'José Ramírez Torres', 'Despacho 15, Planta 3, Edificio Norte'),
('cdominguez', 'Producción', 'cdominguez@empresa.com', 'Carmen Domínguez Sánchez', 'Despacho 18, Planta 2, Edificio Sur'),
('agonzalez', 'Calidad', 'agonzalez@empresa.com', 'Antonio González Pérez', 'Despacho 20, Planta 1, Edificio Este'),
('psantos', 'Logística', 'psantos@empresa.com', 'Pablo Santos Ruiz', 'Despacho 22, Planta 4, Edificio Central'),
('mbenitez', 'Compras', 'mbenitez@empresa.com', 'Marta Benítez López', 'Despacho 25, Planta 3, Edificio Norte'),
('fgarcia', 'Legal', 'fgarcia@empresa.com', 'Fernando García Torres', 'Despacho 30, Planta 5, Edificio Oeste'),
('srodriguez', 'Control', 'srodriguez@empresa.com', 'Sofía Rodríguez Martín', 'Despacho 6, Planta 2, Edificio Sur'),
('dhernandez', 'Administración', 'dhernandez@empresa.com', 'Diego Hernández López', 'Despacho 8, Planta 1, Edificio Este'),
('nruiz', 'Recursos Humanos', 'nruiz@empresa.com', 'Natalia Ruiz Fernández', 'Despacho 11, Planta 4, Edificio Central'),
('jmorales', 'Finanzas', 'jmorales@empresa.com', 'Javier Morales García', 'Despacho 13, Planta 3, Edificio Norte'),
('eperez', 'Marketing', 'eperez@empresa.com', 'Elena Pérez Sánchez', 'Despacho 16, Planta 2, Edificio Sur'),
('rgarcia', 'Ventas', 'rgarcia@empresa.com', 'Roberto García Díaz', 'Despacho 19, Planta 1, Edificio Este'),
('mmolina', 'Producción', 'mmolina@empresa.com', 'Manuel Molina Torres', 'Despacho 21, Planta 4, Edificio Central'),
('lrojas', 'Calidad', 'lrojas@empresa.com', 'Lucía Rojas Gómez', 'Despacho 23, Planta 3, Edificio Norte'),
('jcastro', 'Logística', 'jcastro@empresa.com', 'Jorge Castro Ruiz', 'Despacho 26, Planta 2, Edificio Sur'),
('cfernandez', 'Compras', 'cfernandez@empresa.com', 'Clara Fernández Pérez', 'Despacho 28, Planta 1, Edificio Este'),
('apardo', 'Legal', 'apardo@empresa.com', 'Alberto Pardo Sánchez', 'Despacho 31, Planta 4, Edificio Central'),
('mlopez', 'Control', 'mlopez@empresa.com', 'Mónica López Torres', 'Despacho 33, Planta 3, Edificio Norte'),
('jmartinez', 'Administración', 'jmartinez@empresa.com', 'Julián Martínez Gómez', 'Despacho 35, Planta 2, Edificio Sur'),
('cgarcia', 'Recursos Humanos', 'cgarcia@empresa.com', 'Cristina García Ruiz', 'Despacho 37, Planta 1, Edificio Este'),
('arodriguez', 'Finanzas', 'arodriguez@empresa.com', 'Alejandro Rodríguez Díaz', 'Despacho 39, Planta 4, Edificio Central'),
('mramirez', 'Marketing', 'mramirez@empresa.com', 'Marcos Ramírez López', 'Despacho 41, Planta 3, Edificio Norte'),
('sdominguez', 'Ventas', 'sdominguez@empresa.com', 'Sandra Domínguez Torres', 'Despacho 43, Planta 2, Edificio Sur'),
('agonzalez2', 'Producción', 'agonzalez2@empresa.com', 'Andrés González Pérez', 'Despacho 45, Planta 1, Edificio Este'),
('psantos2', 'Calidad', 'psantos2@empresa.com', 'Patricia Santos Ruiz', 'Despacho 47, Planta 4, Edificio Central');

-- Incidencias de ejemplo (10)
INSERT INTO incidencias (id, resumen, descripcion, servicio, prioridad, estado, fecha_deseada, departamento, usuario_id) VALUES
('10000001', 'Error impresora', 'La impresora del despacho 4 no imprime', 'Soporte', 'Alta', 'Pendiente', '2026-01-10', 'Control', 1),
('10000002', 'Correo bloqueado', 'El usuario no puede acceder a su correo', 'Correo', 'Media', 'Asignado', '2026-01-12', 'Administración', 2),
('10000003', 'Problema red', 'No hay conexión en planta 2', 'Red', 'Alta', 'En curso', '2026-01-15', 'Recursos Humanos', 3),
('10000004', 'Actualización software', 'Se requiere actualización de Office', 'Software', 'Baja', 'Pendiente', '2026-01-20', 'Finanzas', 4),
('10000005', 'Fallo login', 'El usuario no puede iniciar sesión en la intranet', 'Autenticación', 'Alta', 'Pendiente', '2026-01-22', 'Marketing', 5),
('10000006', 'Teléfono desconectado', 'El teléfono de la oficina no funciona', 'Telefonía', 'Media', 'Asignado', '2026-01-25', 'Ventas', 6),
('10000007', 'Pantalla rota', 'El monitor del despacho 18 está dañado', 'Hardware', 'Alta', 'Pendiente', '2026-01-28', 'Producción', 7),
('10000008', 'Acceso denegado', 'El usuario no puede acceder a carpetas compartidas', 'Permisos', 'Media', 'En curso', '2026-01-30', 'Calidad', 8),
('10000009', 'Servidor caído', 'El servidor de archivos no responde', 'Infraestructura', 'Alta', 'Pendiente', '2026-02-02', 'Logística', 9),
('10000010', 'Error base de datos', 'La aplicación no conecta con la base de datos', 'BD', 'Alta', 'Pendiente', '2026-02-05', 'Compras', 10);