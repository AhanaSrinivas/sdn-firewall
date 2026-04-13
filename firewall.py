from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

# MAC learning table
mac_to_port = {}

def _handle_ConnectionUp(event):
    log.info("Switch connected")

def _handle_PacketIn(event):
    packet = event.parsed
    dpid = event.connection.dpid
    in_port = event.port

    if dpid not in mac_to_port:
        mac_to_port[dpid] = {}

    src = packet.src
    dst = packet.dst

    # Learn MAC address
    mac_to_port[dpid][src] = in_port

    ip_packet = packet.find('ipv4')

    # 🔐 FIREWALL RULE
    if ip_packet:
        src_ip = str(ip_packet.srcip)
        dst_ip = str(ip_packet.dstip)

        if src_ip == "10.0.0.1" and dst_ip == "10.0.0.2":
            log.warning(f"BLOCKED: {src_ip} -> {dst_ip}")

            msg = of.ofp_flow_mod()
            msg.match.dl_type = 0x0800
            msg.match.nw_src = ip_packet.srcip
            msg.match.nw_dst = ip_packet.dstip
            msg.priority = 100
            msg.actions = []  # DROP

            event.connection.send(msg)
            return

    # 🔁 LEARNING SWITCH LOGIC
    if dst in mac_to_port[dpid]:
        out_port = mac_to_port[dpid][dst]
    else:
        out_port = of.OFPP_FLOOD

    actions = [of.ofp_action_output(port=out_port)]

    # Install forwarding rule
    if out_port != of.OFPP_FLOOD:
        msg = of.ofp_flow_mod()
        msg.match.dl_dst = dst
        msg.actions = actions
        msg.priority = 10
        event.connection.send(msg)

    # Send packet
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions = actions
    event.connection.send(msg)


def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    log.info("Firewall controller started")