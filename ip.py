import os, sys, socket, time, ipaddress, requests
from datetime import datetime

os.system("title IP Lookup")

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[38;2;100;200;255m"
GREEN  = "\033[38;2;100;255;100m"
YELLOW = "\033[38;2;255;255;120m"
RED    = "\033[38;2;255;75;75m"

def is_ip(addr):
    try: ipaddress.ip_address(addr); return True
    except ValueError: return False

def resolve(host):
    try:
        infos = socket.getaddrinfo(host, None)
        for fam, *_ in infos:
            if fam == socket.AF_INET: return socket.gethostbyname(host)
        return infos[0][4][0]
    except Exception as e:
        raise RuntimeError(f"DNS resolution failed: {e}")

def reverse(ip):
    try: return socket.gethostbyaddr(ip)[0]
    except: return None

def geo_lookup(ip, retries=3, timeout=6):
    url = f"http://ip-api.com/json/{ip}"
    params = {"fields":"status,message,query,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,reverse"}
    last_exc = None
    for _ in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code != 200:
                last_exc = RuntimeError(f"HTTP {r.status_code}")
                time.sleep(0.5)
                continue
            data = r.json()
            if data.get("status") != "success": raise RuntimeError(data.get("message","Unknown"))
            return data
        except Exception as e:
            last_exc = e
            time.sleep(0.5)
    raise RuntimeError(f"Lookup failed after {retries} attempts: {last_exc}")

def show(data, ip, rev, target):
    print(f"\n{BOLD}{CYAN}=== IP INFO ==={RESET}")
    print(f"{GREEN}Input         : {RESET}{target}")
    print(f"{GREEN}Resolved IP   : {RESET}{ip}")
    print(f"{GREEN}Reverse DNS   : {RESET}{rev if rev else 'N/A'}")
    g = lambda k: data.get(k) if data else None
    print(f"{GREEN}Country       : {RESET}{g('country')} ({g('countryCode')})")
    print(f"{GREEN}Region        : {RESET}{g('regionName')} ({g('region')})")
    print(f"{GREEN}City          : {RESET}{g('city')}")
    print(f"{GREEN}Zip           : {RESET}{g('zip')}")
    print(f"{GREEN}Latitude      : {RESET}{g('lat')}")
    print(f"{GREEN}Longitude     : {RESET}{g('lon')}")
    print(f"{GREEN}Timezone      : {RESET}{g('timezone')}")
    print(f"{GREEN}ISP           : {RESET}{g('isp')}")
    print(f"{GREEN}Org           : {RESET}{g('org')}")
    print(f"{GREEN}AS            : {RESET}{g('as')}")
    print(f"{GREEN}Mobile?       : {RESET}{g('mobile')}")
    print(f"{GREEN}Proxy/VPN?    : {RESET}{g('proxy')}")
    print(f"{GREEN}Hosting?      : {RESET}{g('hosting')}")
    print(f"{GREEN}Lookup Time   : {RESET}{datetime.now().isoformat(sep=' ', timespec='seconds')}")

def main():
    try:
        target = input(f"{YELLOW}Target IP->> {RESET}").strip()
        if not target: print(f"{RED}No input provided.{RESET}"); return
        resolved = target if is_ip(target) else resolve(target)
        if not is_ip(target): print(f"{CYAN}[i] Resolved -> {GREEN}{resolved}{RESET}")
        rev = reverse(resolved)
        if rev: print(f"{CYAN}[i] Reverse DNS -> {GREEN}{rev}{RESET}")
        print(f"{CYAN}[i] Performing lookup...{RESET}")
        data = geo_lookup(resolved)
        show(data, resolved, rev, target)
    except KeyboardInterrupt: print(f"\n{RED}Interrupted.{RESET}")
    except Exception as e: print(f"{RED}Error: {e}{RESET}")
    finally:
        try: input(f"{YELLOW}Press Enter to exit...{RESET}")
        except: pass

if __name__ == "__main__": main()
