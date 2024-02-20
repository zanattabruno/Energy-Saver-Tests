from kubernetes import client, config
import os
import yaml
import time

E2TERM_VALUES = '../helm-charts/e2term/values.yaml'
E2SIM_VALUES = '../helm-charts/e2sim-helm/values.yaml'
XAPP_VALUES = '../helm-charts/bouncer-xapp/values.yaml'

E2TERM_SCTP_LIST = [ {'name': 'node2', 'addr': '10.43.0.225', 'port': 30001},{'name': 'node2', 'addr': '10.43.0.226', 'port': 30002}, {'name': 'node3', 'addr': '10.43.0.227', 'port': 30003}]



def read_yaml(path):
    with open(path) as file:
        values = yaml.safe_load(file) 
    return values

def write_yaml(data, path_file):
    with open(path_file, 'w') as file:
        yaml.dump(data, file)


def deploy_e2term():
    config.load_kube_config()

    api_instance = client.CoreV1Api()

    body = {
        "metadata": {
            "labels": {
                "beta.kubernetes.io/arch":"amd64"
                }
        }
    }
    node_list = api_instance.list_node()
    values = read_yaml(E2TERM_VALUES)
    i = 1 
    for node in node_list.items:
        values = read_yaml(E2TERM_VALUES)
        values['nodeSelector']['kubernetes.io/hostname'] = node.metadata.name
        values['services']['sctp']['nodePort']= 30000+i
        write_yaml(values, E2TERM_VALUES)
        if i == len(node_list.items):
            os.system('helm upgrade --install opt-e2term-'+node.metadata.name+' ../helm-charts/e2term/ -n ricplt --wait')
            i = i+1
        else:
            os.system('helm upgrade --install opt-e2term-'+node.metadata.name+' ../helm-charts/e2term/ -n ricplt')
            i = i+1
    time.sleep(30)

def deploy_e2sim():
    config.load_kube_config()

    api_instance = client.CoreV1Api()

    body = {
        "metadata": {
            "labels": {
                "beta.kubernetes.io/arch":"amd64"
                }
        }
    }

    node_list = api_instance.list_node()
    values = read_yaml(E2SIM_VALUES)
    i = 1 
    for node in node_list.items:
        print(node.metadata.name)
        if node.metadata.name != 'node1':
            values = read_yaml(E2SIM_VALUES)
            values['nodeSelector']['kubernetes.io/hostname'] = node.metadata.name
            values['service']['nodePort'] = 31001+i
            values['image']['args']['e2term'] = E2TERM_SCTP_LIST[0]['addr']
            values['image']['args']['port'] = E2TERM_SCTP_LIST[0]['port']
            values['image']['args']['gNB'] = i*100
            values['image']['args']['id'] = i + 1
            write_yaml(values, E2SIM_VALUES)
            if i == len(node_list.items) - 1:
                os.system('helm upgrade --install opt-e2sim-'+node.metadata.name+' ../helm-charts/e2sim-helm -n ricplt --wait')
                i = i+1
            else:
                os.system('helm upgrade --install opt-e2sim-'+node.metadata.name+' ../helm-charts/e2sim-helm -n ricplt')
                i = i+1

def deploy_xApp():
    config.load_kube_config()

    api_instance = client.CoreV1Api()

    body = {
        "metadata": {
            "labels": {
                "beta.kubernetes.io/arch":"amd64"
                }
        }
    }

    node_list = api_instance.list_node()
    values = read_yaml(XAPP_VALUES)
    i = 1 
    for node in node_list.items:
        if node.metadata.name != 'node1':
            values = read_yaml(XAPP_VALUES)
            values['nodeSelector']['kubernetes.io/hostname'] = 'node1'
            values['containers'][0]['args']['gNB'] = i*100
            write_yaml(values, XAPP_VALUES)
            if i == len(node_list.items) - 1:
                os.system('helm upgrade --install opt-xapp-e2node'+str(i+1)+' ../helm-charts/bouncer-xapp -n ricxapp --wait')
                i = i+1
            else:
                os.system('helm upgrade --install opt-xapp-e2node'+str(i+1)+' ../helm-charts/bouncer-xapp -n ricxapp')
                i = i+1

if __name__ == '__main__':
    deploy_e2term()
