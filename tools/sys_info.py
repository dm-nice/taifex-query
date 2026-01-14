import platform
import json
import os
import subprocess
from datetime import datetime

def get_windows_info():
    """獲取 Windows 詳細資訊"""
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             "(Get-CimInstance -ClassName Win32_OperatingSystem).Caption"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

def get_cpu_name():
    """獲取 CPU 名稱"""
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Name"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return platform.processor()
    except:
        return platform.processor()

def get_cpu_speed():
    """獲取 CPU 頻率（GHz）"""
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty MaxClockSpeed"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            mhz = int(result.stdout.strip())
            return round(mhz / 1000, 2)
        return None
    except:
        return None

def get_cpu_usage():
    """獲取 CPU 使用率（Windows）"""
    try:
        if platform.system() == "Windows":
            # 使用 PowerShell 命令獲取 CPU 使用率
            ps_command = "(Get-Counter '\\Processor(_Total)\\% Processor Time').CounterSamples.CookedValue"
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                cpu_value = result.stdout.strip()
                return round(float(cpu_value), 2)
        # 如果無法獲取，返回 None
        return None
    except Exception as e:
        print(f"警告: 無法獲取 CPU 使用率 - {e}")
        return None

def get_memory_info():
    """獲取記憶體資訊（Windows）"""
    try:
        # 獲取總記憶體
        result_total = subprocess.run(
            ['powershell', '-Command',
             "(Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # 獲取可用記憶體
        result_free = subprocess.run(
            ['powershell', '-Command',
             "(Get-CimInstance -ClassName Win32_OperatingSystem).FreePhysicalMemory"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result_total.returncode == 0 and result_free.returncode == 0:
            total_bytes = int(result_total.stdout.strip())
            free_kb = int(result_free.stdout.strip())

            total_gb = round(total_bytes / (1024**3), 2)
            free_gb = round(free_kb / (1024**2), 2)
            used_gb = round(total_gb - free_gb, 2)
            usage_percent = round((used_gb / total_gb) * 100, 2)

            return {
                "total_gb": total_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
                "usage_percent": usage_percent
            }
        return None
    except Exception as e:
        print(f"警告: 無法獲取記憶體資訊 - {e}")
        return None

def get_system_info():
    """收集系統資訊"""
    cpu_usage = get_cpu_usage()
    cpu_name = get_cpu_name()
    cpu_speed = get_cpu_speed()
    windows_info = get_windows_info()
    memory_info = get_memory_info()

    system_info = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "os": {
            "system": windows_info if windows_info else f"{platform.system()} {platform.release()}",
            "version": platform.version(),
            "machine": platform.machine()
        },
        "cpu": {
            "name": cpu_name,
            "speed_ghz": cpu_speed,
            "usage_percent": cpu_usage if cpu_usage is not None else "N/A",
            "cpu_count": os.cpu_count()
        },
        "memory": memory_info if memory_info else "N/A"
    }
    return system_info

def main():
    print("正在收集系統資訊...")

    # 獲取系統資訊
    info = get_system_info()

    # 顯示資訊
    print(f"\n作業系統: {info['os']['system']}")
    print(f"CPU: {info['cpu']['name']}")
    if info['cpu']['speed_ghz']:
        print(f"CPU 頻率: {info['cpu']['speed_ghz']} GHz")
    print(f"CPU 使用率: {info['cpu']['usage_percent']}%")

    # 顯示記憶體資訊
    if info['memory'] != "N/A":
        mem = info['memory']
        print(f"\n記憶體總量: {mem['total_gb']} GB")
        print(f"已使用: {mem['used_gb']} GB ({mem['usage_percent']}%)")
        print(f"可用: {mem['free_gb']} GB")

    # 儲存為 JSON 檔案
    output_file = "report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"\n系統資訊已儲存至 {output_file}")

if __name__ == "__main__":
    main()
