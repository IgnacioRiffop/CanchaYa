-- Generado por Oracle SQL Developer Data Modeler 21.4.2.059.0838
--   en:        2025-10-10 12:34:08 CLST
--   sitio:      Oracle Database 11g
--   tipo:      Oracle Database 11g



-- predefined type, no DDL - MDSYS.SDO_GEOMETRY

-- predefined type, no DDL - XMLTYPE

CREATE TABLE cancha (
    id_cancha                  INTEGER NOT NULL,
    nombre                     NVARCHAR2(50) NOT NULL,
    direccion                  NVARCHAR2(150) NOT NULL,
    imagen                     BLOB NOT NULL,
    hora_inicio                DATE NOT NULL,
    hora_fin                   DATE NOT NULL,
    tipo_cancha_id_tipo_cancha INTEGER NOT NULL
);

ALTER TABLE cancha ADD CONSTRAINT cancha_pk PRIMARY KEY ( id_cancha );

CREATE TABLE equipamiento (
    id_equipamiento INTEGER NOT NULL,
    nombre          NVARCHAR2(150) NOT NULL,
    stock           INTEGER NOT NULL
);

ALTER TABLE equipamiento ADD CONSTRAINT equipamiento_pk PRIMARY KEY ( id_equipamiento );

CREATE TABLE horario (
    id_horario  INTEGER NOT NULL,
    hora_inicio DATE NOT NULL,
    hora_fin    DATE NOT NULL
);

ALTER TABLE horario ADD CONSTRAINT horario_pk PRIMARY KEY ( id_horario );

CREATE TABLE promocion (
    id_promocion INTEGER NOT NULL,
    codigo       NVARCHAR2(10) NOT NULL,
    valor        INTEGER,
    porcentaje   INTEGER
);

ALTER TABLE promocion ADD CONSTRAINT promocion_pk PRIMARY KEY ( id_promocion );

CREATE TABLE reserva (
    id_reserva             INTEGER NOT NULL,
    fecha                  DATE NOT NULL,
    subtotal               INTEGER NOT NULL,
    descuento              INTEGER NOT NULL,
    total                  INTEGER NOT NULL,
    estado                 CHAR(1) NOT NULL,
    cancha_id_cancha       INTEGER NOT NULL,
    usuario_id_usuario     INTEGER NOT NULL,
    promocion_id_promocion INTEGER NOT NULL,
    horario_id_horario     INTEGER NOT NULL
);

ALTER TABLE reserva ADD CONSTRAINT reserva_pk PRIMARY KEY ( id_reserva );

CREATE TABLE reserva_equipamiento (
    equipamiento_id_equipamiento INTEGER NOT NULL,
    reserva_id_reserva           INTEGER NOT NULL,
    cantidad                     INTEGER
);

ALTER TABLE reserva_equipamiento ADD CONSTRAINT reserva_equipamiento_pk PRIMARY KEY ( equipamiento_id_equipamiento,
                                                                                      reserva_id_reserva );

CREATE TABLE tipo_cancha (
    id_tipo_cancha INTEGER NOT NULL,
    nombre         NVARCHAR2(150) NOT NULL
);

ALTER TABLE tipo_cancha ADD CONSTRAINT tipo_cancha_pk PRIMARY KEY ( id_tipo_cancha );

CREATE TABLE usuario (
    id_usuario INTEGER NOT NULL,
    nombre     NVARCHAR2(50) NOT NULL,
    apellido   NVARCHAR2(50) NOT NULL,
    email      NVARCHAR2(100) NOT NULL,
    pass       NVARCHAR2(100) NOT NULL
);

ALTER TABLE usuario ADD CONSTRAINT usuario_pk PRIMARY KEY ( id_usuario );

ALTER TABLE cancha
    ADD CONSTRAINT cancha_tipo_cancha_fk FOREIGN KEY ( tipo_cancha_id_tipo_cancha )
        REFERENCES tipo_cancha ( id_tipo_cancha );

ALTER TABLE reserva_equipamiento
    ADD CONSTRAINT equipamiento_reserva_fk FOREIGN KEY ( reserva_id_reserva )
        REFERENCES reserva ( id_reserva );

ALTER TABLE reserva
    ADD CONSTRAINT reserva_cancha_fk FOREIGN KEY ( cancha_id_cancha )
        REFERENCES cancha ( id_cancha );

ALTER TABLE reserva_equipamiento
    ADD CONSTRAINT reserva_equipamiento_fk FOREIGN KEY ( equipamiento_id_equipamiento )
        REFERENCES equipamiento ( id_equipamiento );

ALTER TABLE reserva
    ADD CONSTRAINT reserva_horario_fk FOREIGN KEY ( horario_id_horario )
        REFERENCES horario ( id_horario );

ALTER TABLE reserva
    ADD CONSTRAINT reserva_promocion_fk FOREIGN KEY ( promocion_id_promocion )
        REFERENCES promocion ( id_promocion );

ALTER TABLE reserva
    ADD CONSTRAINT reserva_usuario_fk FOREIGN KEY ( usuario_id_usuario )
        REFERENCES usuario ( id_usuario );



-- Informe de Resumen de Oracle SQL Developer Data Modeler: 
-- 
-- CREATE TABLE                             8
-- CREATE INDEX                             0
-- ALTER TABLE                             15
-- CREATE VIEW                              0
-- ALTER VIEW                               0
-- CREATE PACKAGE                           0
-- CREATE PACKAGE BODY                      0
-- CREATE PROCEDURE                         0
-- CREATE FUNCTION                          0
-- CREATE TRIGGER                           0
-- ALTER TRIGGER                            0
-- CREATE COLLECTION TYPE                   0
-- CREATE STRUCTURED TYPE                   0
-- CREATE STRUCTURED TYPE BODY              0
-- CREATE CLUSTER                           0
-- CREATE CONTEXT                           0
-- CREATE DATABASE                          0
-- CREATE DIMENSION                         0
-- CREATE DIRECTORY                         0
-- CREATE DISK GROUP                        0
-- CREATE ROLE                              0
-- CREATE ROLLBACK SEGMENT                  0
-- CREATE SEQUENCE                          0
-- CREATE MATERIALIZED VIEW                 0
-- CREATE MATERIALIZED VIEW LOG             0
-- CREATE SYNONYM                           0
-- CREATE TABLESPACE                        0
-- CREATE USER                              0
-- 
-- DROP TABLESPACE                          0
-- DROP DATABASE                            0
-- 
-- REDACTION POLICY                         0
-- 
-- ORDS DROP SCHEMA                         0
-- ORDS ENABLE SCHEMA                       0
-- ORDS ENABLE OBJECT                       0
-- 
-- ERRORS                                   0
-- WARNINGS                                 0
