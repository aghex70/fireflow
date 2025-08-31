from sqlalchemy.exc import IntegrityError


def map_integrity_error(e: IntegrityError) -> tuple[str, int]:
    # e.orig is the DBAPI error (sqlite3.IntegrityError, etc.)
    s = str(getattr(e, "orig", e))  # robust across backends

    if (
        "uq_policy_id_order_index" in s
        or "UNIQUE constraint failed: firewall_rules.policy_id, firewall_rules.order_index"
        in s
    ):
        return "A rule with this order_index already exists in this policy.", 409

    # CHECK: source ports pair and range
    if "ck_src_ports_pair_and_range" in s:
        return (
            "source_port_minimum/maximum must both be null or 1..65535 with min <= max.",
            422,
        )

    # CHECK: destination ports pair and range
    if "ck_dst_ports_pair_and_range" in s:
        return (
            "destination_port_minimum/maximum must both be null or 1..65535 with min <= max.",
            422,
        )

    # CHECK: same IP family for both CIDRs
    if "ck_same_ip_family_if_both_set" in s:
        return "source_cidr and destination_cidr must be both IPv4 or both IPv6.", 422

    # Fallback
    return "Constraint violation.", 422
