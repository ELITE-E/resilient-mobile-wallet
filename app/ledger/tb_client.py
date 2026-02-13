import tigerbeetle as tb
from app.settings.config import settings

def get_tb_client_async() -> tb.ClientAsync:
    # replica_addresses can be "host:port" or just "3000" (localhost default)
    return tb.ClientAsync(
        cluster_id=settings.tb_cluster_id,
        replica_addresses=settings.tb_address,
    )