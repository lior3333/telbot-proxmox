from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException
import os
from config import (
    PROXMOX_HOST,
    PROXMOX_NODE,
    PROXMOX_USER,
    PROXMOX_TOKEN_NAME,
    PROXMOX_TOKEN_VALUE,
    VERIFY_SSL,
)

PROXMOX_NODE = PROXMOX_NODE

class ProxmoxClient:
    def __init__(self):
        self.proxmox = ProxmoxAPI(
            host= PROXMOX_HOST,
            user=PROXMOX_USER,
            token_name=PROXMOX_TOKEN_NAME,
            token_value=PROXMOX_TOKEN_VALUE,
            verify_ssl = VERIFY_SSL #bool
        )

    def list_vms(self):
        vms = self.proxmox.nodes(PROXMOX_NODE).qemu.get()
        return [
            {
                "vmid": vm["vmid"],
                "name": vm["name"],
                "status": vm["status"]
            }
            for vm in vms
        ]
    

    def list_lxc(self):
        containers = self.proxmox.nodes(PROXMOX_NODE).lxc.get()
        return [
            {
                "vmid": ct["vmid"],
                "name": ct["name"],
                "status": ct["status"]
            }
            for ct in containers
        ]

    def list_running_resources(self):
        resources = []

        # VMs (QEMU)
        vms = self.proxmox.nodes(PROXMOX_NODE).qemu.get()
        for vm in vms:
            if vm.get("status") == "running":
                resources.append({
                    "type": "vm",
                    "vmid": vm["vmid"],
                    "name": vm.get("name", ""),
                    "status": vm["status"]
                })

        # LXC Containers
        lxcs = self.proxmox.nodes(PROXMOX_NODE).lxc.get()
        for ct in lxcs:
            if ct.get("status") == "running":
                resources.append({
                    "type": "lxc",
                    "vmid": ct["vmid"],
                    "name": ct.get("name", ""),
                    "status": ct["status"]
                })

        return resources
    
    def vm_exists(self, vmid: int) -> bool:
        self.proxmox.nodes(PROXMOX_NODE).qemu(vmid).config.get()
        return True


    def get_vm_status(self, vmid: int) -> str:
        return self.proxmox.nodes(PROXMOX_NODE)\
        .qemu(vmid)\
        .status.current.get()["status"]
        

    def start_vm(self, vmid: int):
        if self.get_vm_status(vmid) != "running":
            self.proxmox.nodes(PROXMOX_NODE)\
                .qemu(vmid)\
                .status.start.post()
    


    def stop_vm(self, vmid: int) -> str:
        status = self.get_vm_status(vmid)

        if status == "running":
            self.proxmox.nodes(PROXMOX_NODE)\
            .qemu(vmid)\
            .status.stop.post()
            return "stopping"

        return "already_stopped"

    def get_vm_ip(self, vmid: int) -> str:
        try:
            interfaces = self.proxmox.nodes(PROXMOX_NODE).qemu(vmid).agent.network_get_interfaces.get()
            for iface in interfaces.get("result", []):
                for ip_info in iface.get("ip-addresses", []):
                    ip = ip_info.get("ip-address")
                    ip_type = ip_info.get("ip-address-type")
                    if ip_type == "ipv4" and ip != "127.0.0.1":
                        return ip
            return "IP not found"
        except Exception:
            return "QEMU Agent not running or not installed"

    def get_vm_resource_usage(self, vmid: int) -> dict:
        try:
            status = self.proxmox.nodes(PROXMOX_NODE).qemu(vmid).status.current.get()
            
            # CPU usage
            cpu_usage = status.get("cpu", 0) * 100 # Convert to percentage
            max_cpu = status.get("cpus", 1) 
            
            # RAM usage
            mem_used = status.get("mem", 0)
            max_mem = status.get("maxmem", 0)
            mem_usage_percent = (mem_used / max_mem) * 100 if max_mem > 0 else 0
            
            return {
                "cpu_usage": round(cpu_usage, 2),
                "max_cpu": max_cpu,
                "mem_used_u": round(mem_used / (1024 * 1024), 2), # MB
                "max_mem_u": round(max_mem / (1024 * 1024), 2),   # MB
                "mem_usage_percent": round(mem_usage_percent, 2)
            }
        except Exception as e:
            return {
                "error": str(e)
            }

    def list_snapshots(self, vmid: int) -> list:
        try:
            snapshots = self.proxmox.nodes(PROXMOX_NODE).qemu(vmid).snapshot.get()
            # Filter out the 'current' pseudo-snapshot if it exists in the list (Proxmox sometimes returns it)
            return [
                {
                    "name": snap.get("name"),
                    "description": snap.get("description", ""),
                    "snaptime": snap.get("snaptime"),
                    "parent": snap.get("parent", "")
                }
                for snap in snapshots if snap.get("name") != "current"
            ]
        except Exception:
            return []

    def create_snapshot(self, vmid: int, snapname: str, description: str = "") -> str:
        try:
            self.proxmox.nodes(PROXMOX_NODE).qemu(vmid).snapshot.post(
                snapname=snapname,
                description=description
            )
            return "success"
        except Exception as e:
            return str(e)
