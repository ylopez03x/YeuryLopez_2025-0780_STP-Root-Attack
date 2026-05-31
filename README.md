# STP Root Attack
**Autor:** Yeury Lopez de Leon  
**Matrícula:** 2025-0780  
**Materia:** Seguridad de Redes  
**Fecha:** 31/05/2026  

---

## Objetivo del Laboratorio
Demostrar el ataque STP Root Bridge Claim en un entorno 
controlado, evidenciando cómo un atacante puede tomar control 
del árbol de spanning tree para redirigir el tráfico de la red.

---

## Objetivo del Script
Enviar BPDUs falsos con prioridad 1 para que Kali sea elegida 
como Root Bridge, desplazando a SW1 que tiene prioridad 4096.

### Parámetros usados
| Parámetro | Valor | Descripción |
|---|---|---|
| INTERFAZ | eth0 | Interfaz de Kali hacia SW1 |
| BRIDGE_PRIORITY | 1 | Prioridad falsa (menor que SW1=4096) |
| KALI_MAC | 00:50:00:00:00:06 | MAC de Kali como Root Bridge |
| HELLO_TIME | 2 seg | Intervalo de envío de BPDUs |

### Requisitos para utilizar la herramienta
- Kali Linux con Python 3
- Librería Scapy instalada
- Permisos root
- Conectividad capa 2 con los switches
- STP habilitado en los switches objetivo

---

## Documentación del funcionamiento del Script

**1. Obtención de MAC**  
`get_if_hwaddr("eth0")` obtiene la MAC real de Kali para 
usarla como identificador del Root Bridge falso.

**2. Construcción del BPDU**  
Cada paquete contiene:
- Ethernet hacia multicast STP `01:80:c2:00:00:00`
- LLC con DSAP y SSAP 0x42
- BPDU de configuración con prioridad 1 y MAC de Kali

**3. Envío continuo**  
El script envía BPDUs cada 2 segundos (Hello Time de STP) 
para mantener a Kali como Root Bridge activo.

**4. Efecto en la red**  
SW1 y SW2 recalculan la topología STP apuntando a Kali 
como Root, causando inestabilidad y redirección de tráfico.

---

## Documentación de la Red

### Topología
> 📸 **[INSERTAR CAPTURA DE LA TOPOLOGÍA EN EVE-NG]**

### Direccionamiento IP
| Dispositivo | Interfaz | Dirección IP | Máscara | Rol |
|---|---|---|---|---|
| R1 | fa0/0 | 172.25.78.1 | /24 | Gateway + DHCP Server |
| SW1 | VLAN1 | 172.25.78.2 | /24 | Switch Core - Root Bridge |
| SW2 | VLAN1 | 172.25.78.3 | /24 | Switch Acceso |
| Kali | eth0 | 172.25.78.10 | /24 | Atacante |
| PC1 | eth0 | 172.25.78.20 | /24 | Víctima 1 (estática) |
| PC2 | eth0 | 172.25.78.21 | /24 | Víctima 2 (DHCP) |

### Conexiones
| Dispositivo A | Interfaz | Dispositivo B | Interfaz |
|---|---|---|---|
| R1 | fa0/0 | SW1 | e0/0 |
| SW1 | e0/1 | Kali | eth0 |
| SW1 | e0/2 | PC1 | eth0 |
| SW1 | e0/3 | SW2 | e0/0 |
| SW2 | e0/1 | PC2 | eth0 |

### Herramientas utilizadas
- EVE-NG Community Edition
- Cisco IOL L2 v15.1 (SW1, SW2)
- Cisco IOS 3725 v12.4 Dynamips (R1)
- Kali Linux 2024
- Python 3 + Scapy
- VPCS (PC1, PC2)

---

## Capturas de Pantalla

### Topología del laboratorio
> 📸 **[INSERTAR CAPTURA DE LA TOPOLOGÍA]**

### SW1 como Root Bridge antes del ataque
> 📸 **[INSERTAR CAPTURA DE: show spanning-tree vlan 1 en SW1 con "This bridge is the root"]**

### Ejecución del script
> 📸 **[INSERTAR CAPTURA DEL SCRIPT CORRIENDO EN KALI]**

### SW1 pierde el rol de Root Bridge
> 📸 **[INSERTAR CAPTURA DE: show spanning-tree vlan 1 en SW1 sin "This bridge is the root"]**

### Kali como nuevo Root Bridge
> 📸 **[INSERTAR CAPTURA DE: show spanning-tree vlan 1 en SW1 mostrando MAC de Kali como Root]**

---

## Contramedidas

### BPDU Guard en SW1
```cisco
spanning-tree portfast bpduguard default
interface ethernet 0/1
 spanning-tree portfast
 spanning-tree bpduguard enable
```

### Root Guard en SW1
```cisco
interface ethernet 0/3
 spanning-tree guard root
```

### Verificación
> 📸 **[INSERTAR CAPTURA DE: show spanning-tree inconsistentports en SW1]**

### Resultado
BPDU Guard deshabilita automáticamente cualquier puerto que 
reciba BPDUs no autorizados. Root Guard evita que puertos 
específicos acepten un Root Bridge superior al configurado.

> 📸 **[INSERTAR CAPTURA DEL SCRIPT CORRIENDO CON CONTRAMEDIDA ACTIVA]**