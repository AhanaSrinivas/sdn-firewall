from pox.core import core
import pox.openflow.libopenflow_01 as of

# Get the POX logger so the controller can print useful status messages.
log = core.getLogger()

# Store learned MAC-to-port mappings here.
# The outer key is the switch DPID and the inner key is a MAC address.
mac_to_port = {}


# This handler runs when a switch connects to the POX controller.
def _handle_ConnectionUp(event):
    # Record that the switch came online.
    log.info("Switch connected")


# This handler runs every time the switch sends a PacketIn event.
def _handle_PacketIn(event):
    # Parse the raw packet that came from the switch.
    packet = event.parsed
    # Get the datapath ID so we know which switch sent the packet.
    dpid = event.connection.dpid
    # Remember the input port on which the packet arrived.
    in_port = event.port

    # Create a per-switch MAC table the first time we see this switch.
    if dpid not in mac_to_port:
        mac_to_port[dpid] = {}

    # Extract the source and destination MAC addresses from the Ethernet frame.
    src = packet.src
    dst = packet.dst

    # Learn the source MAC address on the ingress port.
    mac_to_port[dpid][src] = in_port

    # Try to find an IPv4 payload inside the packet.
    ip_packet = packet.find('ipv4')

    # Apply the firewall rule only if this is an IPv4 packet.
    if ip_packet:
        # Convert the source IP to a string for easy comparison.
        src_ip = str(ip_packet.srcip)
        # Convert the destination IP to a string for easy comparison.
        dst_ip = str(ip_packet.dstip)

        # Block traffic from h1 to h2.
        if src_ip == "10.0.0.1" and dst_ip == "10.0.0.2":
            # Log the blocked flow so we can see the firewall working.
            log.warning(f"BLOCKED: {src_ip} -> {dst_ip}")

            # Build a flow-mod message that installs a drop rule.
            msg = of.ofp_flow_mod()
            # Match IPv4 packets only.
            msg.match.dl_type = 0x0800
            # Match the blocked source IP.
            msg.match.nw_src = ip_packet.srcip
            # Match the blocked destination IP.
            msg.match.nw_dst = ip_packet.dstip
            # Use a high priority so this rule wins over forwarding rules.
            msg.priority = 100
            # No actions means the packet is dropped.
            msg.actions = []

            # Send the drop rule to the switch.
            event.connection.send(msg)
            # Stop processing because the packet is blocked.
            return

    # If the destination MAC is known, forward to that port.
    if dst in mac_to_port[dpid]:
        # Use the learned output port for the destination host.
        out_port = mac_to_port[dpid][dst]
    else:
        # Flood unknown destinations so the switch can discover them.
        out_port = of.OFPP_FLOOD

    # Build the output action for this packet.
    actions = [of.ofp_action_output(port=out_port)]

    # Install a forwarding rule only when the destination port is known.
    if out_port != of.OFPP_FLOOD:
        # Create a flow-mod message for normal forwarding.
        msg = of.ofp_flow_mod()
        # Match on the destination MAC address.
        msg.match.dl_dst = dst
        # Forward packets using the learned output action.
        msg.actions = actions
        # Give this rule a lower priority than the firewall rule.
        msg.priority = 10
        # Send the forwarding rule to the switch.
        event.connection.send(msg)

    # Create a packet-out message for the current packet.
    msg = of.ofp_packet_out()
    # Attach the packet data that triggered PacketIn.
    msg.data = event.ofp
    # Attach the chosen action list.
    msg.actions = actions
    # Send the packet immediately.
    event.connection.send(msg)


# Register the event handlers when POX loads this module.
def launch():
    # Listen for packets sent up by the switch.
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    # Listen for switch connection events.
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    # Print a startup message so we know the controller launched.
    log.info("Firewall controller started")