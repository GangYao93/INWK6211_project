# import json and yaml module to transfer config to json or yaml format
import json
import yaml

# all router's config saved in a dictionary, whose key is router name and value is a sub-dictionary of config of the router.
# name is hostname of router, to make sure json and yaml file contain the hostname inside the file;
# port_detail_list is a list of ports' config, each element inside this list is a dictionary whose elements
# are port, name, ip address and netmask;
# rip_list contains all networks connected to this router
router_conf_dir = {
    'R1': {
        "name": "R1",
        "port_detail_list": [{"port": "s0/0/0", "ip_address": "192.168.10.1", "netmask": "255.255.255.0"},
                             {"port": "s0/0/1", "ip_address": "192.168.20.1", "netmask": "255.255.255.0"},
                             {"port": "s0/1/0", "ip_address": "192.168.30.1", "netmask": "255.255.255.0"},
                             {"port": "g0/0", "ip_address": "192.168.60.1", "netmask": "255.255.255.0"}],
        "rip_list": ["192.168.10.0", "192.168.20.0", "192.168.30.0", "192.168.60.0"]
    },
    'R2': {
        "name": "R2",
        "port_detail_list": [{"port": "s0/0/0", "ip_address": "192.168.20.2", "netmask": "255.255.255.0"},
                             {"port": "s0/0/1", "ip_address": "192.168.40.1", "netmask": "255.255.255.0"}],
        "rip_list": ["192.168.20.0", "192.168.40.0"]
    },
    'R3': {
        "name": "R3",
        "port_detail_list": [{"port": "s0/0/0", "ip_address": "192.168.30.2", "netmask": "255.255.255.0"},
                             {"port": "s0/0/1", "ip_address": "192.168.50.1", "netmask": "255.255.255.0"}],
        "rip_list": ["192.168.30.0", "192.168.50.0"]
    },
    'R4': {
        "name": "R4",
        "port_detail_list": [{"port": "s0/0/0", "ip_address": "192.168.10.2", "netmask": "255.255.255.0"},
                             {"port": "s0/0/1", "ip_address": "192.168.40.2", "netmask": "255.255.255.0"},
                             {"port": "s0/1/0", "ip_address": "192.168.50.2", "netmask": "255.255.255.0"},
                             {"port": "g0/0", "ip_address": "192.168.70.1", "netmask": "255.255.255.0"}],
        "rip_list": ["192.168.10.0", "192.168.40.0", "192.168.50.0", "192.168.70.0"]
    }
}




# write command of get into global config mode
def enter_global_mode(file):
    file.write("enable\n")
    file.write("config terminal\n")


# config the addresses of each port and let them open
def config_port_ip(file, port_list):
    for port_detail in port_list:
        file.write("int {}\n".format(port_detail["port"]))
        file.write("ip address {} {}\n".format(port_detail["ip_address"], port_detail["netmask"]))
        file.write("no shutdown\n")


# config version 2 of RIP routing protocol to the router and add all network that connect to the router
def config_rip(file, rip_list):
    file.write("router rip\nversion 2\nno auto-summary\n")
    for rip in rip_list:
        file.write("network {}\n".format(rip))


# Save configs of each router in separate files
def save_config():
    # list of allowed file type
    file_type_list = ['txt', 'json', 'yaml']
    # iterate all elements of the dictionary
    for router_name, router_conf in router_conf_dir.items():
        # ask use to input each file type of router's config
        file_type = input('please choose the file type of {}[{}]: '.format(router_name, '/'.join(file_type_list)))
        # give use a hint if the input type is wrong, until user select a right file type
        while file_type not in file_type_list:
            file_type = input('file type [{}] is not exist, please choose the file type of {}[{}]: '.format(file_type, router_name, '/'.join(file_type_list)))
        # create and write config to file
        with open('{}.{}'.format(router_name, file_type), "w") as file:
            # logic of file type is txt, generate and save the config to file
            if file_type == 'txt':
                # calling enter_global_mode function to get into global config mode
                enter_global_mode(file)
                # config of host name
                file.write("hostname {}\n".format(router_name))
                # calling config_port_ip and config_rip to config port address and RIP protocol
                config_port_ip(file, router_conf['port_detail_list'])
                config_rip(file, router_conf['rip_list'])
            # logic of file type is json, directly transfer config to json and save it
            elif file_type == 'json':
                json_str = json.dumps(router_conf)
                file.write(json_str)
            # logic of file type is yaml, directly transfer config to yaml and save it
            elif file_type == 'yaml':
                yaml_str = yaml.dump(router_conf)
                file.write(yaml_str)


# entrance of the script
if __name__ == '__main__':
    # call save_config function to start transfer
    save_config()
