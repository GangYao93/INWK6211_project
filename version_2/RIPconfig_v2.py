# netemiko to build ssh connection to routers
from netmiko import ConnectHandler as ch
# pandas for read excel
import pandas as pd
# logging for record logs
import logging

# use logging module to output logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
# global variable for router config
router_conf_dir = {
}


# read configration from excel
def read_router_conf():
    # use pandas read excel
    excel = pd.ExcelFile('router_conf.xlsx')
    # connect_config sheet for connection parameters
    connect_config = excel.parse('connect_config')
    # interface sheet contains ip config for each port
    interface_config = excel.parse('interface')
    # RIP sheet contains network that connect to the router
    rip_config = excel.parse('RIP')
    # one router only can have one connect_config but can have multiple port or RIP network
    # iterator connect_config sheet to get all configs
    for index, router in connect_config.iterrows():
        hostname = router['host_name']
        logging.info(f'start to read config of {hostname}...')
        # build connect parameter as netmiko format
        connect_detail = {
            'host': router['ip_address'],
            'username': router['username'],
            'password': router['password'],
            'device_type': router['device_type'],
        }
        # Filter out configurations in the interface sheet with the same hostname.
        interface_detail = interface_config[interface_config['host_name'] == hostname]
        interface_list = []
        for _, interface in interface_detail.iterrows():
            interface_list.append({
                'port': interface['port'],
                'ip_address': interface['ip_address'],
                'netmask': interface['netmask']
            })
        # Filter out configurations in the RIP sheet with the same hostname.
        rip_detail = rip_config[rip_config['host_name'] == hostname]
        rip_list = [rip['network'] for _, rip in rip_detail.iterrows()]
        router_conf_dir[hostname] = {
            'name': hostname,
            'port_detail_list': interface_list,
            "rip_list": rip_list,
            'connect_detail': connect_detail
        }
    logging.info('finish reading router conf file')


# write command of get into global config mode
def enter_global_mode(commands):
    commands.append("enable")
    commands.append("config terminal")


# config the addresses of each port and let them open
def config_port_ip(commands, port_list):
    for port_detail in port_list:
        commands.append("int {}".format(port_detail["port"]))
        commands.append("ip address {} {}".format(port_detail["ip_address"], port_detail["netmask"]))
        commands.append("no shutdown")
        commands.append("exit")


# config version 2 of RIP routing protocol to the router and add all network that connect to the router
def config_rip(commands, rip_list):
    commands.append("router rip")
    commands.append("version 2")
    commands.append("no auto-summary")
    for rip in rip_list:
        commands.append("network {}".format(rip))
    commands.append("exit")


def config_router():
    for key, value in router_conf_dir.items():
        # build command list for one router
        commands = []
        enter_global_mode(commands)
        commands.append('hostname {}'.format(key))
        config_port_ip(commands, value['port_detail_list'])
        config_rip(commands, value['rip_list'])
        try:
            # connect to router by user netmiko
            connection = ch(**value['connect_detail'])
            # apply all commands to router
            connection.send_config_set(commands)
            # save commands to startup-config
            connection.save_config()
            # disconnect to release resource
            connection.disconnect()
        except Exception as e:
            # if some error occurs during config, give some message to use and jump to next router
            logging.error('failed to send config to router {}:{}'.format(key,e))
            continue


# entrance of the script
if __name__ == '__main__':
    # call save_config function to start transfer
    read_router_conf()
    config_router()
