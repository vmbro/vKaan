#  Copyright 2024 vKaan MP, vmbro.com
#  Author: Onur Yuzseven
import logging
from typing import Any
from typing import List
from aria.ops.object import Object
from aria.ops.result import CollectResult
from aria.ops.suite_api_client import SuiteApiClient
from constants import VCENTER_ADAPTER_KIND
from pyVmomi import vim

logger = logging.getLogger(__name__)

def add_cluster_metrics(
    suite_api_client: SuiteApiClient,
    adapter_instance_id: str,
    result: CollectResult,
    content: Any,
) -> None:
    container = content.rootFolder
    view_type = [vim.ClusterComputeResource]
    recursive = True
    container_view = content.viewManager.CreateContainerView(
        container, view_type, recursive
    )

    # Retrieve object types from the Aria Operations
    clusters: List[Object] = suite_api_client.query_for_resources(
        {
            "adapterKind": [VCENTER_ADAPTER_KIND],
            "resourceKind": ["ClusterComputeResource"],
            "adapterInstanceId": [adapter_instance_id],
        }
    )

    # Match the Aria Operations objects with the related identifier
    clusters_by_uuid: dict[str, Object] = {
        cluster.get_identifier_value("VMEntityObjectID"): cluster for cluster in clusters
    }

    # Push your metrics below
    children = container_view.view
    for cluster in children:
        cluster_obj = clusters_by_uuid.get(cluster._moId)
        if cluster_obj:
            if cluster.configuration.dasConfig.hostMonitoring == 'enabled':
                hostMonitoring = True
            else:
                hostMonitoring = False

            cluster_obj.with_property("configuration|dasConfig|Host Monitoring", bool(hostMonitoring))
            cluster_obj.with_property("configuration|dasConfig|Response \ Host Isolation", str(cluster.configuration.dasConfig.defaultVmSettings.isolationResponse))
            cluster_obj.with_property("configuration|dasConfig|Response \ Default VM Restart Priority", str(cluster.configuration.dasConfig.defaultVmSettings.restartPriority))
            cluster_obj.with_property("configuration|dasConfig|Response \ Datastore APD", str(cluster.configuration.dasConfig.defaultVmSettings.vmComponentProtectionSettings.vmStorageProtectionForAPD))
            cluster_obj.with_property("configuration|dasConfig|Response \ Datastore PDL", str(cluster.configuration.dasConfig.defaultVmSettings.vmComponentProtectionSettings.vmStorageProtectionForPDL))
            cluster_obj.with_property("configuration|dasConfig|VM Monitoring", str(cluster.configuration.dasConfig.vmMonitoring))         
            cluster_obj.with_property("configuration|dasConfig|Heartbeat Datastore", str(cluster.configuration.dasConfig.hBDatastoreCandidatePolicy))
            cluster_obj.with_property("configuration|drsConfig|Proactive DRS", str(cluster.configurationEx.proactiveDrsConfig.enabled))
            cluster_obj.with_property("configuration|drsConfig|Scale Descendants Shares", str(cluster.configuration.drsConfig.scaleDescendantsShares))
            cluster_obj.with_metric("configuration|drsConfig|DRS Score (%)", int(cluster.summary.drsScore))
            result.add_object(cluster_obj)
        else:
            logger.warning(
                f"Could not find Cluster '{cluster.name}' with MoID: {cluster._moId}."
            )