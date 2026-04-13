# 🔐 SDN-Based Firewall using POX Controller

## 📌 Overview
This project implements a Software Defined Networking (SDN) based firewall using the POX controller and Mininet. The firewall inspects traffic at the controller level and dynamically installs flow rules in the switch to allow or block communication between hosts.

The project demonstrates how centralized control in SDN enables flexible and programmable network security.

---

## 🎯 Objective
The objectives of this project are:
- To block communication between specific hosts using IP-based filtering
- To allow normal communication between other hosts
- To demonstrate dynamic flow rule installation
- To implement match–action logic using OpenFlow
- To log blocked traffic for monitoring

---

## 🏗️ Network Topology

The network consists of:
- 1 Switch (s1)
- 3 Hosts (h1, h2, h3)

### IP Addressing

| Host | IP Address |
|------|-----------|
| h1   | 10.0.0.1  |
| h2   | 10.0.0.2  |
| h3   | 10.0.0.3  |

This simple topology ensures clear observation of firewall behavior without additional routing complexity.

### Topology Justification
A single-switch topology is used to simplify the network design and eliminate routing complexity. This allows clear visualization of controller–switch interaction and makes it easier to demonstrate firewall behavior such as blocking and allowing traffic without interference from multi-hop paths.

---

## ⚙️ Setup Instructions

### 1. Install Dependencies
sudo apt update  
sudo apt install mininet git -y  

### 2. Clone POX Controller
git clone https://github.com/noxrepo/pox.git  
cd pox  

---

## ▶️ Execution Steps

### Step 1: Start POX Controller
cd ~/pox  
./pox.py log.level --DEBUG firewall  

The controller listens for switch connections and processes incoming packets.

---

### Step 2: Start Mininet (New Terminal)
sudo mn -c  
sudo mn --topo single,3 --controller=remote,ip=127.0.0.1,port=6633  

This creates:
- 3 hosts (h1, h2, h3)
- 1 switch (s1)
- Remote connection to the POX controller

---

## 🔐 Firewall Policy

- Block: 10.0.0.1 → 10.0.0.2  
- Allow: All other traffic  

---

## ⚙️ Working Principle

1. When a packet arrives at the switch:
   - If no matching rule exists, it is sent to the controller (PacketIn event)

2. The controller:
   - Extracts source and destination IP addresses
   - Compares them with the firewall policy

3. Based on the decision:
   - Blocked traffic → installs a drop rule (no action)
   - Allowed traffic → installs a forwarding rule

4. After rule installation:
   - Future packets are handled directly by the switch
   - Controller load is reduced

---

## 🔁 Flow Rule Design

Two types of flow rules are used:

Firewall Rule:
- Priority: 100
- Match: Source IP = 10.0.0.1, Destination IP = 10.0.0.2
- Action: Drop

Forwarding Rule:
- Priority: 10
- Match: MAC/IP fields
- Action: Forward to appropriate port

Higher priority ensures that firewall rules override normal forwarding rules.

---

## 🧪 Testing

Allowed Traffic:  
h1 ping h3  
Result: Successful communication, no packet loss  

Blocked Traffic:  
h1 ping h2  
Result: 100% packet loss, communication blocked  

---

## 📊 Performance Analysis

Throughput Measurement:  
h1 iperf -s &  
h3 iperf -c h1  

Observation:
- High throughput for allowed traffic
- Blocked traffic cannot establish connection

Latency Measurement:  
h1 ping h3  

Observation:
- Low latency after flow rules are installed

### Performance Explanation
The first packet of any new flow is sent to the controller for processing. Once the controller installs the appropriate flow rule in the switch, subsequent packets are handled directly by the switch without involving the controller. This reduces delay, minimizes controller overhead, and results in improved throughput and lower latency for allowed traffic.

---

## 📋 Flow Table Verification

sudo ovs-ofctl dump-flows s1  

Expected output includes:
- High priority drop rule for blocked traffic
- Forwarding rules for allowed traffic

---

## 📜 Controller Logs

Example:  
BLOCKED: 10.0.0.1 -> 10.0.0.2  

This confirms that the firewall is actively monitoring and enforcing rules.

---

## 📊 Observations

- Flow rules are dynamically installed by the controller
- The first packet is processed by the controller
- Subsequent packets are handled by the switch
- Firewall rules successfully block unauthorized communication
- Allowed traffic is not affected
- Network performance remains efficient

---

## 🧠 Concepts Demonstrated

- Software Defined Networking (SDN)
- Separation of control plane and data plane
- OpenFlow protocol
- Match–Action flow rules
- PacketIn and FlowMod handling
- Centralized network control

---

## 📁 Project Structure

sdn-firewall/  
 ├── firewall.py  
 ├── README.md  
 └── screenshots/  

---

## ✅ Conclusion

This project demonstrates how SDN can be used to implement a flexible and efficient firewall. By centralizing control in the controller, network policies can be dynamically enforced without modifying individual devices.

The implementation highlights the advantages of SDN, including programmability, scalability, and improved network security.

---