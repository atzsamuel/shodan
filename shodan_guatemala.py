#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para consultar Shodan filtrando por Guatemala y mostrar resumen.
Autor: Samuel Atz
Carnet: [TU CARNET]
Curso: Seguridad Informática
Sección: [TU SECCIÓN]
"""

import os
import sys
from collections import defaultdict
import shodan

QUERY = 'country:"GT"'  # Filtro para Guatemala (sin usar org:)

def fail(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def main():
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        fail("No se encontró SHODAN_API_KEY en el entorno. Exporta tu API key: export SHODAN_API_KEY='tu_api_key'")

    api = shodan.Shodan(api_key)

    # 1) Verificar cuenta / permisos / créditos
    try:
        info = api.info()  # devuelve información de la cuenta
        # info ej.: {'query_credits': 100, 'scan_credits': 0, 'usage_limits': {...}, ...}
    except shodan.APIError as e:
        # 401/403 suelen caer aquí con mensaje útil
        fail(f"No fue posible consultar info de cuenta (¿API key válida?): {e}")

    query_credits = info.get("query_credits", 0)
    if query_credits <= 0:
        fail("Tu cuenta no tiene créditos de búsqueda (query_credits=0) o tu plan no permite /shodan/host/search. Revisa/actualiza tu plan.")

    # 2) Ejecutar búsqueda
    try:
        results = api.search(QUERY)
    except shodan.APIError as e:
        # Mensajes típicos: 'Access denied (403 Forbidden)', 'Upgrade your API plan' etc.
        fail(f"Error en la consulta: {e}")

    # 3) Procesar resultados
    ip_set = set()
    ips_por_puerto = defaultdict(set)

    print("Resultados para Guatemala (country:GT):\n")
    for i, r in enumerate(results.get("matches", []), start=1):
        ip = r.get("ip_str") or r.get("ip")
        port = r.get("port")
        city = (r.get("location") or {}).get("city")
        product = r.get("product")
        print(f"[{i}] IP: {ip} | Puerto: {port} | Ciudad: {city} | Servicio: {product}")

        if ip:
            ip_set.add(ip)
            if port is not None:
                ips_por_puerto[port].add(ip)

    # 4) Resumen
    print("\nResumen:")
    print("Carnet: [TU CARNET]")
    print("Nombre: Samuel Atz")
    print("Curso: Seguridad Informática")
    print("Sección: [TU SECCIÓN]")
    print(f"Total de direcciones IP identificadas: {len(ip_set)}")

    print("Total de IPs por puerto abierto:")
    if not ips_por_puerto:
        print("  (No se identificaron puertos en los resultados)")
    else:
        for port in sorted(ips_por_puerto.keys()):
            print(f"  Puerto {port}: {len(ips_por_puerto[port])} IPs")

if __name__ == "__main__":
    main()