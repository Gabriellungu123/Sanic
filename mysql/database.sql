DROP DATABASE IF EXISTS incidencias_db;
CREATE DATABASE incidencias_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE incidencias_db;

CREATE TABLE grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE semigrupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    grupo_id INT NOT NULL,

    FOREIGN KEY (grupo_id) REFERENCES grupos(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    rol ENUM('superadmin', 'admin', 'tecnico', 'cliente') NOT NULL,
    grupo_id INT NULL,
    semigrupo_id INT NULL,

    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    FOREIGN KEY (semigrupo_id) REFERENCES semigrupos(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE incidencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,

    resumen VARCHAR(180) NOT NULL,
    descripcion TEXT NOT NULL,
    contacto VARCHAR(150) NOT NULL,

    estado ENUM('Asignado', 'En curso', 'Pendiente', 'Cerrado', 'Cancelado', 'Resuelta') DEFAULT 'Asignado',
    prioridad ENUM('Baja', 'Media', 'Alta', 'Urgente') DEFAULT 'Media',

    cliente_id INT NOT NULL,
    grupo_id INT NOT NULL,
    semigrupo_id INT NOT NULL,
    tecnico_id INT NULL,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (cliente_id) REFERENCES usuarios(id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    FOREIGN KEY (semigrupo_id) REFERENCES semigrupos(id),
    FOREIGN KEY (tecnico_id) REFERENCES usuarios(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incidencia_id INT NOT NULL,
    usuario_id INT NOT NULL,
    comentario TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO grupos (codigo, nombre) VALUES
('GRP-001', 'Informatica'),
('GRP-002', 'Recursos Humanos'),
('GRP-003', 'Mantenimiento'),
('GRP-004', 'Administracion'),
('GRP-005', 'Seguridad');

INSERT INTO semigrupos (codigo, nombre, grupo_id) VALUES
('SEM-001', 'Soporte', 1),
('SEM-002', 'Redes', 1),
('SEM-003', 'Sistemas', 1),

('SEM-004', 'Contratacion', 2),
('SEM-005', 'Nominas', 2),
('SEM-006', 'Formacion', 2),

('SEM-007', 'Electricidad', 3),
('SEM-008', 'Climatizacion', 3),
('SEM-009', 'Limpieza', 3),

('SEM-010', 'Facturacion', 4),
('SEM-011', 'Compras', 4),
('SEM-012', 'Archivo', 4),

('SEM-013', 'Control de acceso', 5),
('SEM-014', 'Camaras', 5),
('SEM-015', 'Emergencias', 5);

INSERT INTO usuarios (nombre, username, email, password, rol, grupo_id, semigrupo_id) VALUES
('Super Admin', 'super.admin', 'superadmin@test.com', '1234', 'superadmin', NULL, NULL),

('Carlos Martin', 'carlos.martin', 'admin.info1@test.com', '1234', 'admin', 1, 1),
('Laura Gomez', 'laura.gomez', 'admin.info2@test.com', '1234', 'admin', 1, 1),
('Daniel Ruiz', 'daniel.ruiz', 'tec.info1@test.com', '1234', 'tecnico', 1, 1),
('Marta Lopez', 'marta.lopez', 'tec.info2@test.com', '1234', 'tecnico', 1, 2),
('Sergio Perez', 'sergio.perez', 'tec.info3@test.com', '1234', 'tecnico', 1, 3),
('Ana Torres', 'ana.torres', 'tec.info4@test.com', '1234', 'tecnico', 1, 1),
('Javier Molina', 'javier.molina', 'tec.info5@test.com', '1234', 'tecnico', 1, 2),

('Alberto Cano', 'alberto.cano', 'admin.rrhh1@test.com', '1234', 'admin', 2, 4),
('Nuria Silva', 'nuria.silva', 'admin.rrhh2@test.com', '1234', 'admin', 2, 4),
('Raul Moreno', 'raul.moreno', 'tec.rrhh1@test.com', '1234', 'tecnico', 2, 4),
('Lucia Ramos', 'lucia.ramos', 'tec.rrhh2@test.com', '1234', 'tecnico', 2, 5),
('Hugo Santos', 'hugo.santos', 'tec.rrhh3@test.com', '1234', 'tecnico', 2, 6),
('Irene Castro', 'irene.castro', 'tec.rrhh4@test.com', '1234', 'tecnico', 2, 4),
('Pablo Vidal', 'pablo.vidal', 'tec.rrhh5@test.com', '1234', 'tecnico', 2, 5),

('Miguel Ortega', 'miguel.ortega', 'admin.mant1@test.com', '1234', 'admin', 3, 7),
('Elena Navarro', 'elena.navarro', 'admin.mant2@test.com', '1234', 'admin', 3, 7),
('Mario Vega', 'mario.vega', 'tec.mant1@test.com', '1234', 'tecnico', 3, 7),
('Sara Dominguez', 'sara.dominguez', 'tec.mant2@test.com', '1234', 'tecnico', 3, 8),
('Adrian Romero', 'adrian.romero', 'tec.mant3@test.com', '1234', 'tecnico', 3, 9),
('Cristina Leon', 'cristina.leon', 'tec.mant4@test.com', '1234', 'tecnico', 3, 7),
('David Herrero', 'david.herrero', 'tec.mant5@test.com', '1234', 'tecnico', 3, 8),

('Ruben Gil', 'ruben.gil', 'admin.adm1@test.com', '1234', 'admin', 4, 10),
('Beatriz Vega', 'beatriz.vega', 'admin.adm2@test.com', '1234', 'admin', 4, 10),
('Jorge Marin', 'jorge.marin', 'tec.adm1@test.com', '1234', 'tecnico', 4, 10),
('Paula Medina', 'paula.medina', 'tec.adm2@test.com', '1234', 'tecnico', 4, 11),
('Ivan Fuentes', 'ivan.fuentes', 'tec.adm3@test.com', '1234', 'tecnico', 4, 12),
('Noelia Rios', 'noelia.rios', 'tec.adm4@test.com', '1234', 'tecnico', 4, 10),
('Oscar Campos', 'oscar.campos', 'tec.adm5@test.com', '1234', 'tecnico', 4, 11),

('Antonio Vega', 'antonio.vega', 'admin.seg1@test.com', '1234', 'admin', 5, 13),
('Clara Pardo', 'clara.pardo', 'admin.seg2@test.com', '1234', 'admin', 5, 13),
('Marcos Soler', 'marcos.soler', 'tec.seg1@test.com', '1234', 'tecnico', 5, 13),
('Teresa Roman', 'teresa.roman', 'tec.seg2@test.com', '1234', 'tecnico', 5, 14),
('Victor Nieto', 'victor.nieto', 'tec.seg3@test.com', '1234', 'tecnico', 5, 15),
('Rocio Arias', 'rocio.arias', 'tec.seg4@test.com', '1234', 'tecnico', 5, 13),
('Diego Pastor', 'diego.pastor', 'tec.seg5@test.com', '1234', 'tecnico', 5, 14),

('Cliente Uno', 'cliente.uno', 'cliente1@test.com', '1234', 'cliente', NULL, NULL),
('Cliente Dos', 'cliente.dos', 'cliente2@test.com', '1234', 'cliente', NULL, NULL),
('Cliente Tres', 'cliente.tres', 'cliente3@test.com', '1234', 'cliente', NULL, NULL),
('Cliente Cuatro', 'cliente.cuatro', 'cliente4@test.com', '1234', 'cliente', NULL, NULL),
('Cliente Cinco', 'cliente.cinco', 'cliente5@test.com', '1234', 'cliente', NULL, NULL);

INSERT INTO incidencias 
(codigo, resumen, descripcion, contacto, estado, prioridad, cliente_id, grupo_id, semigrupo_id, tecnico_id)
VALUES
(
    'INC-A1B2C3',
    'No funciona el ordenador',
    'El equipo no enciende correctamente y el usuario no puede trabajar.',
    'cliente1@test.com',
    'Asignado',
    'Alta',
    (SELECT id FROM usuarios WHERE username = 'cliente.uno'),
    1,
    1,
    (SELECT id FROM usuarios WHERE username = 'daniel.ruiz')
),
(
    'INC-D4E5F6',
    'Problema con nomina',
    'El cliente indica que hay un error en la nomina mensual.',
    'cliente2@test.com',
    'En curso',
    'Media',
    (SELECT id FROM usuarios WHERE username = 'cliente.dos'),
    2,
    5,
    (SELECT id FROM usuarios WHERE username = 'lucia.ramos')
),
(
    'INC-G7H8I9',
    'Aire acondicionado roto',
    'La sala principal no tiene climatizacion.',
    'cliente3@test.com',
    'Pendiente',
    'Urgente',
    (SELECT id FROM usuarios WHERE username = 'cliente.tres'),
    3,
    8,
    (SELECT id FROM usuarios WHERE username = 'sara.dominguez')
);

INSERT INTO incidencias
(
    codigo,
    resumen,
    descripcion,
    contacto,
    estado,
    prioridad,
    cliente_id,
    grupo_id,
    semigrupo_id,
    tecnico_id
)
WITH RECURSIVE numeros AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numeros
    WHERE n < 30
),
clientes_ordenados AS (
    SELECT
        id,
        ROW_NUMBER() OVER (ORDER BY id) AS numero_cliente
    FROM usuarios
    WHERE rol = 'cliente'
),
tecnicos_ordenados AS (
    SELECT
        id,
        grupo_id,
        ROW_NUMBER() OVER (PARTITION BY grupo_id ORDER BY id) AS numero_tecnico
    FROM usuarios
    WHERE rol = 'tecnico'
)
SELECT
    CONCAT('INC-SG', LPAD(s.id, 2, '0'), '-', LPAD(n.n, 3, '0')) AS codigo,

    CONCAT('Incidencia ', n.n, ' de ', s.nombre) AS resumen,

    CONCAT(
        'Esta es una incidencia de prueba creada para el semigrupo ',
        s.nombre,
        ' dentro del grupo ',
        g.nombre,
        '.'
    ) AS descripcion,

    CONCAT(
        'contacto_',
        LOWER(REPLACE(REPLACE(s.nombre, ' ', '_'), '.', '')),
        '_',
        n.n,
        '@test.com'
    ) AS contacto,

    CASE
        WHEN n.n % 5 = 0 THEN 'Pendiente'
        WHEN n.n % 5 = 1 THEN 'Asignado'
        WHEN n.n % 5 = 2 THEN 'En curso'
        WHEN n.n % 5 = 3 THEN 'Resuelta'
        ELSE 'Cerrado'
    END AS estado,

    CASE
        WHEN n.n % 4 = 0 THEN 'Urgente'
        WHEN n.n % 4 = 1 THEN 'Alta'
        WHEN n.n % 4 = 2 THEN 'Media'
        ELSE 'Baja'
    END AS prioridad,

    c.id AS cliente_id,
    g.id AS grupo_id,
    s.id AS semigrupo_id,
    t.id AS tecnico_id

FROM semigrupos s
INNER JOIN grupos g ON s.grupo_id = g.id
CROSS JOIN numeros n
INNER JOIN clientes_ordenados c 
    ON c.numero_cliente = ((n.n - 1) % 5) + 1
INNER JOIN tecnicos_ordenados t 
    ON t.grupo_id = g.id
    AND t.numero_tecnico = ((n.n - 1) % 5) + 1;

INSERT INTO comentarios (incidencia_id, usuario_id, comentario)
SELECT
    i.id,
    i.cliente_id,
    CONCAT('Comentario inicial del cliente para la incidencia ', i.codigo)
FROM incidencias i;

INSERT INTO comentarios (incidencia_id, usuario_id, comentario)
SELECT
    i.id,
    i.tecnico_id,
    CONCAT('El tecnico asignado revisara la incidencia ', i.codigo)
FROM incidencias i
WHERE i.tecnico_id IS NOT NULL;

CREATE OR REPLACE VIEW vista_incidencia_por_semigrupo AS
SELECT
    g.codigo AS codigo_grupo,
    g.nombre AS grupo,
    s.codigo AS codigo_semigrupo,
    s.nombre AS semigrupo,
    i.codigo AS codigo_incidencia,
    i.resumen,
    cliente.nombre AS cliente,
    tecnico.nombre AS tecnico_asignado,

    (
        SELECT GROUP_CONCAT(admins.nombre SEPARATOR ', ')
        FROM usuarios admins
        WHERE admins.rol = 'admin'
        AND admins.grupo_id = g.id
    ) AS admins_del_grupo

FROM semigrupos s
INNER JOIN grupos g ON s.grupo_id = g.id
INNER JOIN incidencias i ON i.semigrupo_id = s.id
INNER JOIN usuarios cliente ON i.cliente_id = cliente.id
LEFT JOIN usuarios tecnico ON i.tecnico_id = tecnico.id

WHERE i.id = (
    SELECT MIN(i2.id)
    FROM incidencias i2
    WHERE i2.semigrupo_id = s.id
)

ORDER BY g.id, s.id;