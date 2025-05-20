from kubernetes import client, config
import uuid, time


class LeaderElector:
    def __init__(self, namespace: str, name: str, on_started: callable):
        # Load in-cluster or kubeconfig automatically
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        self.api = client.CoordinationV1Api()
        self.lock_name = name
        self.namespace = namespace
        self.identity = str(uuid.uuid4())
        self.on_started = on_started

    def _make_lease(self):
        return client.V1Lease(
            metadata=client.V1ObjectMeta(name=self.lock_name, namespace=self.namespace),
            spec=client.V1LeaseSpec(
                holder_identity=self.identity,
                lease_duration_seconds=15
            )
        )

    def run(self):
        lease_body = self._make_lease()
        while True:
            try:
                # Try to create or replace the Lease
                try:
                    self.api.create_namespaced_lease(self.namespace, lease_body)
                except client.exceptions.ApiException as e:
                    if e.status == 409:
                        # already exists -> replace
                        self.api.replace_namespaced_lease(
                            self.lock_name, self.namespace, lease_body
                        )
                    else:
                        raise
                # If we succeeded in create/replace, we are the leader
                self.on_started()
            except Exception as e:
                # Log / swallow errors, retry
                print(f"Leader election error: {e}")
            # wait before renewing
            time.sleep(10)
