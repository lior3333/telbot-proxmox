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
