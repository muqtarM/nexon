import os
from typing import Optional, Dict, Any
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException
from nexon_cli.utils.logger import logger
from kubernetes.client import (
            V1Ingress,
            V1IngressSpec,
            V1IngressBackend,
            V1IngressServiceBackend,
            V1IngressRule,
            V1HTTPIngressPath,
            V1HTTPIngressRuleValue,
            V1ObjectMeta,
            NetworkingV1Api,
            V1ServiceBackendPort,
            AutoscalingV1Api,
            V1HorizontalPodAutoscaler,
            V1HorizontalPodAutoscalerSpec,
            V1LabelSelector,
            V1CrossVersionObjectReference,
        )


class ClusterError(Exception):
    pass


class ClusterManager:
    """
     Manages Kubernetes / cloud deployments of Nexon environments.
    """

    def __init__(self):
        # Try in-cluster, then kubeconfig
        try:
            k8s_config.load_incluster_config()
        except Exception:
            k8s_config.load_kube_config()
        self.api = client.CoreV1Api()
        self.apps = client.AppsV1Api()
        self.net = client.NetworkingV1Api()

    def deploy(self,
               env_name: str,
               namespace: Optional[str] = None,
               image: Optional[str] = None,
               cpu: str = "500m",
               memory: str = "1Gi",
               replicas: int = 1,
               env_vars: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Create or update a Deployment + Service for `env_name`.
        """
        ns = namespace or env_name
        # 1) Ensure namespace exists
        try:
            self.api.read_namespace(ns)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                meta = client.V1Namespace(metadata=client.V1ObjectMeta(name=ns))
                self.api.create_namespace(meta)
                logger.info(f"Created namespace '{ns}'")
            else:
                raise ClusterError(e)

        # 2) Build Deployment spec
        img = image or f"nexon/{env_name}:latest"
        container = client.V1Container(
            name=env_name,
            image=img,
            resources=client.V1ResourceRequirements(
                limits={"cpu": cpu, "memory": memory},
                requests={"cpu": cpu, "memory": memory}
            ),
            env=[client.V1EnvVar(name=k, value=v) for k, v in (env_vars or {}).items()]
        )
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": env_name}),
            spec=client.V1PodSpec(containers=[container])
        )
        spec = client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels={"app": env_name}),
            template=template
        )
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=env_name, namespace=ns),
            spec=spec
        )

        # 3) Apply Deployment (create or patch)
        try:
            self.apps.read_namespaced_deployment(env_name, ns)
            self.apps.patch_namespaced_deployment(env_name, ns, deployment)
            action = "Updated"
        except client.exceptions.ApiException as e:
            if e.status == 404:
                self.apps.create_namespaced_deployment(ns, deployment)
                action = "Created"
            else:
                raise ClusterError(e)

        # 4) Expose via ClusterIP Service
        svc = client.V1Service(
            metadata=client.V1ObjectMeta(name=env_name, namespace=ns),
            spec=client.V1ServiceSpec(
                selector={"app": env_name},
                ports=[client.V1ServicePort(port=80, target_port=8000)]
            )
        )
        try:
            self.api.read_namespaced_service(env_name, ns)
            self.api.patch_namespaced_service(env_name, ns, svc)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                self.api.create_namespaced_service(ns, svc)
            else:
                raise ClusterError(e)

        logger.info(f"{action} Deployment & Service for '{env_name}' in namespace '{ns}'")
        return {"namespace": ns, "image": img, "replicas": replicas}

    def expose(self, name: str, host: str, path: str):
        # Create or replace an Ingress
        backend = V1IngressBackend(
            service=V1IngressServiceBackend(
                name=name,
                port=V1ServiceBackendPort(number=80)
            )
        )
        path_obj = V1HTTPIngressPath(path=path, backend=backend)
        rule = V1IngressRule(host=host, http=V1HTTPIngressRuleValue(paths=[path_obj]))
        spec = V1IngressSpec(rules=[rule])
        ingress = V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=V1ObjectMeta(name=name),
            spec=spec
        )

        try:
            self.net.create_namespaced_ingress(namespace="default", body=ingress)
        except ApiException as e:
            if e.status == 409:
                self.net.replace_namespaced_ingress(name=name, namespace="default", body=ingress)
            else:
                raise ClusterError(e)

    def destroy(self, env_name: str, namespace: Optional[str] = None):
        ns = namespace or env_name
        # Delete Service
        try:
            self.api.delete_namespaced_service(env_name, ns)
        except client.exceptions.ApiException:
            pass
        # Delete Deployment
        try:
            self.apps.delete_namespaced_deployment(env_name, ns)
        except client.exceptions.ApiException:
            pass
        # Optionally delete namespace
        # self.api.delete_namespace(ns)
        logger.info(f"Destroyed deployment & service for '{env_name}' in namespace '{ns}'")

    def list(self, namespace: Optional[str] = None) -> Any:
        """
        List all deployments in given namespace or across all.
        """
        if namespace:
            deps = self.apps.list_namespaced_deployment(namespace)
        else:
            deps = self.apps.list_deployment_for_all_namespaces()
        return [(d.metadata.name, d.metadata.namespace, d.status.available_replicas or 0)
                for d in deps.items]

    def create_ingress(
            self,
            env_name: str,
            host: str,
            path: str = "/",
            namespace: Optional[str] = None,
            port: int = 80
    ) -> Dict[str, str]:
        """
        Create or update an Ingress resource for this env_name.
        """
        ns = namespace or env_name

        ingress_name = f"{env_name}-ingress"

        # Build the Ingress object
        ingress = V1Ingress(
            metadata=V1ObjectMeta(name=ingress_name, namespace=ns),
            spec=V1IngressSpec(
                rules=[
                    V1IngressRule(
                        host=host,
                        http=V1HTTPIngressRuleValue(
                            paths=[
                                V1HTTPIngressPath(
                                    path=path,
                                    path_type="Prefix",
                                    backend=V1IngressBackend(
                                        service=V1IngressServiceBackend(
                                            name=env_name,
                                            port=V1ServiceBackendPort(number=port)
                                        )
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        )

        api = NetworkingV1Api()
        try:
            api.replace_namespaced_ingress(ingress_name, ns, ingress)
            action = "Updated"
        except client.exceptions.ApiException as e:
            if e.status == 404:
                api.create_namespaced_ingress(ns, ingress)
                action = "Created"
            else:
                raise ClusterError(e)

        logger.info(f"{action} Ingress '{ingress_name}' -> host={host}{path}")
        return {"ingress": ingress_name, "host": host}

    def autoscale(
            self,
            env_name: str,
            min_replicas: int,
            max_replicas: int,
            cpu_pct: int = 80,
            namespace: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Create or update an HPA for env_name.
        """
        ns = namespace or env_name
        hpa_name = f"{env_name}-hpa"

        # Build HPA Object
        hpa = V1HorizontalPodAutoscaler(
            metadata=V1ObjectMeta(name=hpa_name, namespace=ns),
            spec=V1HorizontalPodAutoscalerSpec(
                scale_target_ref=V1CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=env_name
                ),
                min_replicas=min_replicas,
                max_replicas=max_replicas,
                target_cpu_utilization_percentage=cpu_pct
            )
        )

        api = AutoscalingV1Api()
        try:
            api.replace_namespaced_horizontal_pod_autoscaler(hpa_name, ns, hpa)
            action = "Update"
        except client.exceptions.ApiException as e:
            if e.status == 404:
                api.create_namespaced_horizontal_pod_autoscaler(ns, hpa)
                action = "Created"
            else:
                raise ClusterError(e)

        logger.info(f"{action} HPA '{hpa_name}': {min_replicas}-{max_replicas}@{cpu_pct}%")
        return {"hpa": hpa_name, "min": min_replicas, "max": max_replicas}

    def remove_autoscale(self, env_name: str, namespace: Optional[str] = None):
        ns = namespace or env_name
        api = AutoscalingV1Api()
        hpa_name = f"{env_name}-hpa"
        try:
            api.delete_namespaced_horizontal_pod_autoscaler(hpa_name, ns)
            logger.info(f"Deleted HPA for '{env_name}' in '{ns}'")
        except client.exceptions.ApiException as e:
            if e.status != 404:
                raise ClusterError(e)
