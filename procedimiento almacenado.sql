--CREA TABLA VENTAS USUARIOS PARA ALMACENAR PROCEDIMIENTO
CREATE TABLE ventas_usuario(
    producto_id NUMBER,
    nombre_producto VARCHAR2(255),
    cantidad_vendida NUMBER,
    total_venta NUMBER,
    fecha_venta DATE
);

--CREA UN CURSOR PARA GENERAR UN INFORME UN RESUMEN DE LAS VENTAS DE LOS USUARIOS TIPO RESUMEN DE UN PRODUCTO
CREATE OR REPLACE PROCEDURE generar_informe_ventas_usuario(p_usuario_id IN NUMBER) AS
BEGIN

    DELETE FROM ventas_usuario;

    INSERT INTO ventas_usuario (producto_id, nombre_producto, cantidad_vendida, total_venta, fecha_venta)
    SELECT 
        p.id AS producto_id,
        p.nombre AS nombre_producto,
        SUM(ci.cantidad) AS cantidad_vendida,
        SUM(ci.cantidad * p.precio) AS total_venta,
        MAX(pp.fecha_pedido) AS fecha_venta  
    FROM 
        PRODUCTOS_PEDIDO pp
    JOIN 
        PRODUCTOS_CARRITOITEM ci ON pp.carrito_id = ci.carrito_id
    JOIN 
        PRODUCTOS_PRODUCTO p ON ci.producto_id = p.id
    WHERE 
        pp.estado = 'Pagado' AND 
        p.creador_id = p_usuario_id  
    GROUP BY 
        p.id, p.nombre
    ORDER BY 
        MAX(pp.fecha_pedido) DESC  
    FETCH FIRST 3 ROWS ONLY;  

    COMMIT;
END generar_informe_ventas_usuario;