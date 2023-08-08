from w3 import fork_chain, teardown


def new_chain():
    snapshot_id = 0
    try:
        snapshot_id = fork_chain()
        yield snapshot_id
    finally:
        print(f"Tearing down {snapshot_id}")
        teardown(snapshot_id)
